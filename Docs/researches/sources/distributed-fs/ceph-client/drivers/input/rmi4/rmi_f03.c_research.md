# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f03.c

## Purpose

`rmi_f03.c` implements Synaptics RMI4 Function 03, a PS/2 pass-through function. It exposes a `SERIO_PS_PSTHRU` port so the Linux serio stack and PS/2 consumers can talk to a guest PS/2 device behind an RMI sensor. It also provides helper entry points used by GPIO button functions to overwrite and commit out-of-band trackstick button state.

## Important APIs, Types, and Functions

`struct f03_data` stores the owning `rmi_function`, allocated `serio` port, registration state, overwritten button bitmask, device count, and RX queue length. `rmi_f03_overwrite_button()` and `rmi_f03_commit_buttons()` are integration hooks for F30/F3A trackstick button emulation. `rmi_f03_pt_write()`, `rmi_f03_pt_open()`, and `rmi_f03_pt_close()` are the serio callbacks. `rmi_f03_initialize()` parses F03 query registers, while `rmi_f03_attention()` forwards RMI output-buffer bytes to `serio_interrupt()`.

## Control Flow

Probe allocates `f03_data`, reads the F03 query registers, stores it as function driver data, and defers serio registration until config. On first config, `rmi_f03_register_pt()` allocates and registers the pass-through serio port; later configs only enable the function interrupt bit. Opening the serio port drains pending output-buffer data and enables the F03 IRQ mask. Attention handling consumes transport-supplied attention data when present, otherwise reads the output buffers directly, then reports every valid byte with timeout/parity flags. Closing clears the IRQ mask, and remove unregisters the serio port.

## State and Persistence Behavior

The persistent runtime state is the devm-managed `f03_data`, the explicitly allocated serio port, and the current overwritten button bitmask. The RMI device owns the actual PS/2 TX/RX registers. IRQ enablement is tied to serio open/config state, not only probe state. Button overwrites are held in memory and emitted as `SERIO_OOB_DATA` only when committed.

## Dependencies and Integration Points

The file depends on RMI core transport helpers, the function-handler model, Linux serio, and `rmi_driver_data.attn_data`. It integrates with PS/2 consumers through `serio_register_port()`, and with F30/F3A through the exported overwrite/commit helpers declared in `rmi_driver.h`.

## Risks and Edge Cases

The query fallback for first-generation sensors hardcodes one device and queue length seven. Attention data shorter than the computed output-buffer length is ignored after warning, so packet framing from transport drivers matters. The serio port is allocated with non-devm allocation and released by `serio_unregister_port()`, so remove paths must only unregister once. OOB button commits call into the attached serio driver while RX is paused, which depends on correct serio locking behavior.

## Test Signals

Useful tests include PS/2 mouse/keyboard passthrough enumeration, writes through the serio port, open/close IRQ mask transitions, attention handling with transport-supplied and register-read data, parity/timeout flag propagation, first-generation query fallback, multiple-device warning coverage, and F30/F3A trackstick button overwrite delivery.
