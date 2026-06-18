<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/Kconfig

## Purpose

This Kconfig file exposes the MaxLinear/Intel Lightning Mountain CGU clock driver on x86 or compile-test builds.

## Important APIs, Types, And Functions

`CLK_LGM_CGU` depends on OF, I/O memory, and x86/compile-test; it selects MFD syscon and early flattened OF support. The help text identifies the driver as the Clock Generation Unit for the LGM network processor SoC.

## Control Flow

The symbol controls the LGM object list in the Makefile.

## State And Persistence Behavior

No runtime state exists here. Selecting the symbol makes the LGM CGU platform driver available.

## Dependencies And Integration Points

It integrates OF/syscon dependencies into an x86 clock-controller path.

## Risks And Test Signals

Risks are missing OF/syscon support on x86 configs. Build with `COMPILE_TEST` and boot an LGM DT to verify `intel,cgu-lgm` probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Kconfig -->
