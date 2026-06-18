# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.c

## Purpose
`main.c` is the PCMCIA-facing entry point for the IPWireless 3G card driver. It matches supported cards, allocates the per-device `ipw_dev`, configures I/O and memory windows, wires the hardware, network, and tty layers together, registers the interrupt handler, and tears everything down on remove.

## Important APIs, Types, And Functions
- `ipw_ids` matches manufacturer/card IDs `0x02f2:0x0100` and `0x02f2:0x0200`.
- Module parameters `debug`, `loopback`, and `out_queue` control verbose logging, raw RAS tty visibility, and PPP hardware queue depth.
- `ipwireless_probe` requests I/O space, common memory, attribute memory, maps both windows, and detects V2/V3 cards by common-memory window size.
- `config_ipwireless` sets PCMCIA flags, initializes reboot work, initializes hardware, requests IRQs, creates network and tty contexts, performs V2/V3 hardware initialization, and enables the device last.
- `ipwireless_attach`, `ipwireless_detach`, `release_ipwireless`, `init_ipwireless`, and `exit_ipwireless` own device/module lifecycle.

## Control Flow And State
Module load initializes the tty driver before registering the PCMCIA driver. A matching card allocates `struct ipw_dev`, stores it in `link->priv`, creates hardware state, and calls `config_ipwireless`. Configuration loops through PCMCIA tuples, maps device windows, initializes the hardware with common/attribute memory and a reboot callback, requests IRQs, creates PPP/network and tty layers, and calls `pcmcia_enable_device` only after interrupt consumers are ready.

The reboot path is asynchronous: hardware calls `signalled_reboot_callback`, which schedules work that calls `pcmcia_reset_card` in process context. Removal releases PCMCIA resources, frees tty devices before network, then frees hardware and `ipw_dev`.

## State And Persistence Behavior
`struct ipw_dev` holds PCMCIA link state, card version detection, mapped attribute/common memory, hardware/network/tty pointers, and reboot work. Resources persist only for the configured-card lifetime. Module parameters are global runtime state and affect all devices.

## Dependencies And Integration Points
The file depends on PCMCIA services, kernel I/O resource APIs, workqueues, and local `hardware.h`, `network.h`, `main.h`, and `tty.h`. It connects PCMCIA lifecycle to `ipwireless_interrupt`, `ipwireless_network_create`, and `ipwireless_tty_create`.

## Risks And Edge Cases
The post-probe error path often returns `-1` instead of the original error. Partial failures after network or tty creation rely on detach cleanup. The code assumes PCMCIA resources 2 and 3 are valid memory windows. The final `pcmcia_enable_device` ordering is important because enabling earlier could expose interrupts before network/tty setup.

## Test Signals
Check module load/unload, probe/remove, resource cleanup after failures, `ttyIPWp*` device creation, PPP channel availability after modem open, IRQ delivery through the hardware layer, and card reset through the scheduled reboot work.
