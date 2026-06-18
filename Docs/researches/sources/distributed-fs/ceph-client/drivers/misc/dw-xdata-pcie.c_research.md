# sources/distributed-fs/ceph-client/drivers/misc/dw-xdata-pcie.c

Purpose: implements a PCI driver for the Synopsys DesignWare xData PCIe traffic-generation/performance block. It registers a misc device with sysfs attributes to start/stop read or write traffic and report measured throughput.

Important APIs, types, and functions: `struct dw_xdata_regs` maps the device register layout; `struct dw_xdata` stores BAR mapping, max read/write lengths, mutex, PCI device, and miscdevice. `dw_xdata_start()` programs continuous traffic, `dw_xdata_stop()` clears repeat mode, `dw_xdata_perf()` measures counters over 100 ms, and sysfs `read`/`write` attributes both start/stop traffic on store and return MB/s on show. `dw_xdata_pcie_probe()` and `dw_xdata_pcie_remove()` manage PCI/misc lifecycle.

Control flow: probe enables the PCI device with managed helpers, maps BAR 0, sets bus master, allocates state, computes transfer lengths from PCIe MPS and read request size, allocates an IDA id, creates a named miscdevice, initializes RAM address/port and target endpoint memory address, stores drvdata, and registers the misc device. Writing `1` to `read` or `write` stops existing traffic, clears status, enables continuous burst, sets pattern and control direction/length bits, waits briefly, and checks `STATUS_DONE`. Writing `0` stops traffic. Reading sysfs counters disables perf capture, snapshots counters and jiffies, enables perf, waits 100 ms, snapshots again, computes MB/s, and re-enables perf.

State and persistence: runtime state includes the mapped register BAR, max transfer lengths, misc name/id, and mutex. Hardware state persists in xData registers such as target address, burst count, control, status, RAM registers, performance control, and read/write counters until stopped or removed.

Dependencies and integration points: depends on PCI core, DesignWare/Synopsys PCI IDs, miscdevice, sysfs attribute groups, IDA, mutexes, and PCIe helper APIs `pcie_get_mps()` and `pcie_get_readrq()`. User space controls it through `/sys/class/misc/dw-xdata-pcie.N/{read,write}`.

Risks: sysfs show functions sleep for 100 ms under the device mutex. `dw_xdata_pcie_remove()` parses the ID back from `misc_dev.name`; if parsing fails it returns before stopping/deregistering, which would be hazardous if the name were ever malformed. Traffic targets BAR physical address plus a fixed endpoint memory offset and assumes the hardware design maps that memory. There is no interrupt/error recovery path beyond status polling.

Test signals: PCI probe/remove for the Synopsys EDDA ID, miscdevice creation, sysfs start/stop for read and write, nonzero throughput reporting, concurrent sysfs access serialization, remove while traffic is active, and validation of target address/length programming on actual xData hardware.
