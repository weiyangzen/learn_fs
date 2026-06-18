# sources/distributed-fs/ceph-client/net/qrtr/Kconfig

## Purpose
This Kconfig file declares build-time options for Qualcomm IPC Router support and its endpoint transports. QRTR provides datagram-style communication with services on Qualcomm system components.

## Important APIs, Types, And Functions
The config symbols are `QRTR`, `QRTR_SMD`, `QRTR_TUN`, and `QRTR_MHI`. `QRTR` is the core AF_QIPCRTR protocol. `QRTR_SMD` enables RPMSG/SMD channels, `QRTR_TUN` enables a userspace misc-device endpoint, and `QRTR_MHI` enables MHI channels for external modems.

## Control Flow
There is no runtime control flow in this file. Build selection gates which source files are compiled by the QRTR Makefile. Transport options are only visible inside `if QRTR`, so transport drivers cannot be selected without core QRTR support.

## State And Persistence
This file contributes only Kconfig state. Selected options become kernel build configuration and module availability; they do not define runtime persistence.

## Dependencies And Integration Points
`QRTR_SMD` depends on `RPMSG` or compile-test without RPMSG. `QRTR_MHI` depends on `MHI_BUS`. `QRTR_TUN` has no extra dependency. The help text notes that service lookups require a userspace daemon maintaining a service listing, even though this tree also includes an in-kernel nameservice implementation.

## Risks
Misconfigured builds can include core QRTR without a transport, yielding local socket support but no external endpoint. `QRTR_SMD`'s compile-test condition allows build coverage when RPMSG is absent, so runtime assumptions must remain guarded in the driver.

## Test Signals
Build matrix signals are core-only, SMD with RPMSG, TUN, MHI with MHI_BUS, modular versus built-in combinations, and compile-test coverage for SMD.
