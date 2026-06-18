# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/Kconfig

## Purpose

`Kconfig` declares the kernel configuration symbol for the Chelsio T4/T5 iWARP/RDMA driver. It controls whether the `iw_cxgb4` RDMA upper-layer driver is built into the kernel, built as a module, or omitted.

## Important APIs, Types, and Functions

- `config INFINIBAND_CXGB4` is a tristate option named "Chelsio T4/T5 RDMA Driver".
- The symbol depends on `CHELSIO_T4`, `INET`, and `INFINIBAND_ADDR_TRANS`.
- It selects `CHELSIO_LIB` and `GENERIC_ALLOCATOR`.
- The help text identifies the resulting module name as `iw_cxgb4`.

## Control Flow

There is no runtime control flow. During Kconfig resolution, the option is visible only when the base Chelsio T4 Ethernet driver, IPv4/INET support, and RDMA address translation are enabled. When selected as `y` or `m`, the Makefile receives `CONFIG_INFINIBAND_CXGB4` and builds the `iw_cxgb4` object set accordingly. `select CHELSIO_LIB` ensures shared Chelsio helper code is available.

## State and Persistence Behavior

The file creates persistent build configuration state through `.config`. That state determines whether the driver is linked built-in, emitted as `iw_cxgb4.ko`, or excluded. It does not define runtime driver state.

## Dependencies and Integration Points

The config symbol integrates the RDMA subsystem with the Chelsio Ethernet/offload stack. `CHELSIO_T4` supplies low-level adapter services and ULD registration, `INET` supplies TCP/IP infrastructure used by iWARP connection management, `INFINIBAND_ADDR_TRANS` supplies RDMA address resolution, `CHELSIO_LIB` supplies shared Chelsio library helpers, and `GENERIC_ALLOCATOR` supports resource allocation patterns used by the driver.

## Risks and Edge Cases

The `select CHELSIO_LIB` line forces that helper library without exposing all of its own dependency choices here, so dependency drift in Chelsio library code can surface as build failures. The prompt names only T4/T5 generation support; if source support expands to newer adapters, help text may lag. `depends on INET` excludes non-INET builds even if other RDMA pieces are present, which is expected for iWARP but is still a build-matrix gate.

## Test Signals

Build matrix checks should cover `INFINIBAND_CXGB4=y`, `=m`, and disabled, including dependency-disabled cases for `CHELSIO_T4`, `INET`, and `INFINIBAND_ADDR_TRANS`. Module builds should produce `iw_cxgb4.ko`; built-in builds should link all listed objects without unresolved Chelsio or RDMA symbols.
