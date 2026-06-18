## sources/distributed-fs/ceph-client/drivers/fpga/Makefile

Purpose: this Makefile maps FPGA Kconfig symbols to kernel objects and composes the multi-object Intel DFL FME and AFU drivers.

Important build entries: `obj-$(CONFIG_FPGA)` builds `fpga-mgr.o`; manager drivers include Altera CvP/passive-serial/SoCFPGA, Xilinx core/selectmap/SPI/Zynq/ZynqMP/Versal, Lattice, Microchip, TS73xx, and PR-IP core objects. Bridge entries build `fpga-bridge.o`, SoCFPGA bridges, freeze bridge, and Xilinx PR decoupler. Region entries build `fpga-region.o` and `of-fpga-region.o`. DFL entries build `dfl.o`, FME child drivers, AFU, PCI, N3000 Nios, and tests.

Control flow and integration: the object list mirrors the layered FPGA framework: core manager class, concrete managers, bridge class, bridge drivers, region class, DFL enumeration, then DFL feature devices. `dfl-fme-objs` aggregates `dfl-fme-main.o`, `dfl-fme-pr.o`, `dfl-fme-error.o`, and `dfl-fme-perf.o` into the FME module. `dfl-afu-objs` aggregates AFU main, MMIO region, DMA region, and error reporting into one AFU module.

State and persistence behavior: the file has no runtime state, but object composition defines symbol visibility and module init order. Splitting DFL FME into one compound object means PR, error, thermal/power, perf, and header feature operations are registered together by the FME platform driver, while manager/bridge/region helper drivers are separate modules.

Dependencies and risks: the Makefile assumes Kconfig dependencies prevent missing-framework builds. If a new DFL subfeature source is added without updating compound object lists, it will silently be omitted from the module. Conversely, adding an object under the wrong config can expose symbols or module aliases when the associated framework is unavailable.

Test signals: verify `make drivers/fpga/` with modular and built-in DFL combinations, inspect generated modules for expected aliases (`dfl-fme`, `dfl-port`, `dfl-fme-mgr`, `dfl-fme-bridge`, `dfl-fme-region`), and confirm KUnit test object inclusion only under `CONFIG_FPGA_KUNIT_TESTS`.
