# sources/distributed-fs/ceph-client/drivers/net/hyperv/Makefile

### Purpose
This Makefile wires `CONFIG_HYPERV_NET` to the composite `hv_netvsc.o` driver object.

### Important APIs, Types, And Functions
There are no runtime APIs. The important build variables are `obj-$(CONFIG_HYPERV_NET)` and `hv_netvsc-y`. The composite object includes `netvsc_drv.o`, `netvsc.o`, `rndis_filter.o`, `netvsc_trace.o`, and `netvsc_bpf.o`.

### Control Flow
When `CONFIG_HYPERV_NET` is enabled, Kbuild creates `hv_netvsc.o` from the listed component objects and either links it into vmlinux or emits a module, depending on the tristate value.

### State And Persistence Behavior
The file controls build composition only. It has no runtime state or persistence.

### Dependencies And Integration Points
It integrates with Kbuild and the `HYPERV_NET` symbol from `Kconfig`. The object list defines the module boundary shared by datapath, RNDIS filter, tracepoints, and XDP/BPF support.

### Risks
Any new source file for the Hyper-V net driver must be added here or it will not build. Removing or renaming objects must be coordinated with exported symbols across the component files.

### Test Signals
Compile with `CONFIG_HYPERV_NET=m` and inspect that one `hv_netvsc.ko` is produced with all component object code linked. Built-in compile should also succeed.
