# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-dbg.c

## Purpose
DebugFS support for the Freescale QUICC Engine FHCI host controller. It tracks USB interrupt causes and exposes FHCI controller registers and interrupt statistics under the USB debugfs root.

## Important APIs, types, and functions
`fhci_dbg_isr()` increments per-interrupt counters, using slot 12 for idle-only when `usb_er == -1`. `fhci_dfs_regs_show()` emits key `qe_usb_ctlr` registers and line state. `fhci_dfs_irq_stat_show()` emits named interrupt counters. `fhci_dfs_create()` creates the per-device debugfs directory and `regs`/`irq_stat` files. `fhci_dfs_destroy()` recursively removes them.

## Control flow
The FHCI interrupt path calls `fhci_dbg_isr()` with the event register value. Debugfs reads call the seq-file show functions, which read MMIO registers with `in_8()`/`in_be16()` and return formatted snapshots. Driver initialization/teardown calls create/destroy for the debugfs nodes.

## State and persistence behavior
State is `fhci->usb_irq_stat[]`, `fhci->dfs_root`, and live hardware register contents. Counters persist for the HCD lifetime and are reset only by allocation/reinitialization.

## Dependencies and integration points
Depends on `fhci.h`, Linux debugfs/seq_file, USB debug root, QUICC Engine USB register layout, and `fhci_ioports_check_bus_state()`. It is diagnostic and does not alter controller state.

## Risks and edge cases
Debugfs creation errors are not checked, which is typical but means diagnostics may silently be absent. Counter updates are not synchronized, so debug reads may race interrupt updates and provide approximate values. Register reads assume the controller remains mapped and alive while debugfs files exist.

## Test signals
Debugfs node creation/removal, register read output, interrupt counter increments for each bit and idle-only, repeated bind/unbind, debugfs reads during interrupt activity, and reads after teardown ordering are useful signals.
