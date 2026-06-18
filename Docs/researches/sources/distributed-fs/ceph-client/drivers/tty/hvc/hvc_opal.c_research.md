# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_opal.c

## Purpose
`hvc_opal.c` connects OPAL firmware consoles on PowerNV systems to the HVC core. It supports raw OPAL consoles and OPAL HVSI consoles, handles early boot console discovery from the device tree, and registers a platform driver for runtime console devices.

## Important APIs, Types, and Functions
`struct hvc_opal_priv` stores protocol selection and optional `struct hvsi_priv`. `hvc_opal_raw_ops` maps directly to `opal_get_chars()`, `opal_put_chars()`, and `opal_flush_chars()`. `hvc_opal_hvsi_ops` wraps `hvsilib_get_chars()`, `hvsilib_put_chars()`, `hvsilib_open()`, `hvsilib_close()`, modem control, and IRQ notifier behavior.

Runtime device handling is in `hvc_opal_probe()` and `hvc_opal_remove()`. Early console setup is in `hvc_opal_init_early()`, with udbg support through `udbg_opal_putc()`, `udbg_opal_getc_poll()`, `udbg_opal_getc()`, and debug init variants for raw/HVSI.

## Control Flow
Early init locates `/chosen/stdout` or OPAL console nodes, reads the `reg` terminal number, chooses raw or HVSI ops by compatible string, initializes boot HVSI if needed, installs udbg callbacks, adds preferred `hvc`, and calls `hvc_instantiate(index, index, ops)`. Runtime probe repeats protocol selection for platform devices, reuses the boot private object if appropriate, otherwise allocates private state and instantiates index-to-terminal mapping. It maps an OF IRQ or requests an OPAL console event IRQ, then allocates the HVC device with shared IRQ flags.

## State and Persistence Behavior
The global `hvc_opal_privs[]` maps terminal numbers to private protocol state. `hvc_opal_boot_priv` and `hvc_opal_boot_termno` preserve early console state across runtime probe. Removal calls `hvc_remove()` and frees non-boot private objects.

## Dependencies and Integration Points
It depends on OPAL firmware APIs, Open Firmware device nodes, platform devices, IRQ mapping, `hvc_irq.c`, and `hvsi_lib.c`. The udbg hooks integrate with PowerPC early debug paths.

## Risks and Edge Cases
Terminal numbers index fixed arrays and are bounded by `MAX_NR_HVC_CONSOLES` only in early init; runtime device-tree term numbers must be sane. OPAL event IRQ fallback is used when no interrupt property exists. HVSI put operations use `opal_put_chars_atomic()` to avoid packet interleaving. Duplicate terminal numbers are rejected.

## Test Signals
Signals include device-tree matching for `ibm,opal-console-raw` and `ibm,opal-console-hvsi`, early boot `hvc` output, udbg input/output, OPAL event fallback, shared IRQ delivery, HVSI handshake and modem control, and clean removal of platform devices.
