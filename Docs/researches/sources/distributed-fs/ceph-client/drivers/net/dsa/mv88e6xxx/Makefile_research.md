# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Makefile

## Purpose

This Makefile lists the object composition for the Marvell 88E6xxx DSA switch driver. It builds a single composite `mv88e6xxx.o` from core chip logic, global register blocks, port/PHY/PCS/SerDes support, switchdev, devlink, tracing, TC flower/TCAM support, and optional PTP and LED objects.

## Important APIs, Types, And Targets

`obj-$(CONFIG_NET_DSA_MV88E6XXX) += mv88e6xxx.o` attaches the composite object to the base Kconfig symbol. `mv88e6xxx-objs` includes required objects such as `chip.o`, `devlink.o`, `global1.o`, `global1_atu.o`, `global1_vtu.o`, `global2.o`, `global2_avb.o`, `global2_scratch.o`, `pcs-6185.o`, `pcs-6352.o`, `pcs-639x.o`, `phy.o`, `port.o`, `port_hidden.o`, `serdes.o`, `smi.o`, `switchdev.o`, `trace.o`, `tcflower.o`, and `tcam.o`. Conditional additions include `hwtstamp.o` and `ptp.o` for `CONFIG_NET_DSA_MV88E6XXX_PTP`, and `leds.o` for `CONFIG_NET_DSA_MV88E6XXX_LEDS`. `CFLAGS_trace.o := -I$(src)` makes the local trace header discoverable.

## Control Flow

The Makefile has build control flow only: Kbuild includes the composite object when the base symbol is enabled and appends optional feature objects when their symbols are enabled. The resulting module or built-in object exposes the complete mv88e6xxx driver implementation.

## State And Persistence Behavior

There is no runtime state in this file. Build configuration controls persistent artifacts in the kernel build tree, including whether PTP timestamping and LED control code is linked.

## Dependencies And Integration Points

The file depends on Kconfig symbols from `mv88e6xxx/Kconfig` and Kbuild composite-object semantics. It integrates feature-specific objects with common driver code and sets a local include path needed by the tracing framework.

## Risks

Object list ordering can matter when initialization sections or trace definitions rely on symbols being present. Optional feature objects must remain synchronized with Kconfig dependencies and source-level `#ifdef` expectations. Missing `CFLAGS_trace.o` would break trace header discovery for tracing builds.

## Test Signals

Build the driver as built-in and module with base-only, PTP-enabled, LED-enabled, and combined configurations. Confirm `mv88e6xxx.o` includes expected optional objects and that `trace.o` compiles with its local include path.
