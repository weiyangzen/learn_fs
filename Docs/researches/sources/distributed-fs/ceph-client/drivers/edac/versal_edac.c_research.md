# sources/distributed-fs/ceph-client/drivers/edac/versal_edac.c

Purpose: `versal_edac.c` supports Xilinx/AMD Versal DDRMC ECC through DDRMC/NOC MMIO plus firmware event callbacks. It registers an interrupt-mode EDAC MC, decodes CE/UE logs, reconstructs addresses from ADEC maps, and optionally exposes debugfs injection.

Important APIs/types/functions: `struct edac_priv` stores MMIO bases, counters, status, MC ID, ADEC maps, and debugfs. `get_error_info()` reads/clears CE/UE status. `convert_to_physical()` rebuilds addresses. `handle_error()` reports EDAC. `err_callback()` handles firmware events. `mc_probe()` and `mc_remove()` manage lifecycle.

Control flow: probe maps `base` and `noc`, checks ECC, computes an OF-order ID, derives ranks/channels, allocates EDAC layers, registers the MC, registers PM event callbacks, initializes debug maps if enabled, and enables DDRMC IRQ masks. Callback maps firmware masks to CE/UE, gathers logs, reports, clears ISR, and logs totals.

State and persistence: per-device runtime state holds counters, status, address maps, and debugfs. Hardware status remains until cleared under PCSR unlock/lock. No disk persistence exists.

Dependencies/integration: OF compatible `xlnx,versal-ddrmc`, named MMIO resources, Xilinx firmware event manager, EDAC core, debugfs, and PCSR locking.

Risks: first CE high-row extraction appears to use the low register; UE injection writes one flip register twice and misses another; EDAC page/offset fields are zero; address conversion relies on maps that are built only in debug code in this file; event unwind must be correct.

Test signals: firmware CE/UE events, channel 0/1 register logs, PCSR lock handling, ECC-disabled probe, debugfs CE/UE injection, and unregister/remove ordering.
