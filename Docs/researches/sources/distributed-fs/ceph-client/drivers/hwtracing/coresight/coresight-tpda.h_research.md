# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.h

## Purpose

`coresight-tpda.h` defines the TPDA register map, bit fields, maximum port count, driver state, and sysfs attribute wrapper used by the TPDA CoreSight aggregator driver.

## Important APIs, Types, and Functions

Definitions cover `TPDA_CR`, per-port control registers, FPID, SYNCR, and flush control. Bit fields describe global flush, FREQ timestamping and request interfaces, FLAG and async trigger interfaces, ATID encoding, CMB channel mode, port enable, and DSB/CMB element sizes. `struct tpda_drvdata` stores MMIO base, device handles, lock, ATID, element sizes, cross-trigger booleans, CMB channel mode, SYNCR mode, and count. `enum tpda_cr_mem` and `struct tpda_trig_sysfs_attribute` drive generic sysfs show/store for boolean control fields.

## Control Flow

The C file uses these definitions to assemble global TPDA control before enabling any port, configure per-port element sizes, and expose boolean controls through `tpda_trig_sysfs_rw`. `TPDA_MAX_INPORTS` bounds the architectural port model used by the device.

## State and Persistence Behavior

The header defines the persistent TPDA shadow state. Most booleans are stored in `tpda_drvdata` and only become hardware state when enable paths write `TPDA_CR`. Element-size fields are scratch values discovered from connected TPDM devices during per-port enable and cleared before each lookup.

## Dependencies and Integration Points

It depends on common kernel bit macros and CoreSight types included by the C file. It integrates directly with `coresight-tpda.c` and indirectly with TPDM because element-size fields encode TPDM dataset output widths.

## Risks and Edge Cases

Field definitions must match hardware, especially `TPDA_CR_ATID` and element-size bit encodings. The anonymous compound-literal macro for sysfs attributes relies on static storage behavior through the containing attribute list usage pattern; future refactors should preserve lifetime assumptions.

## Test Signals

Build tests should catch macro and enum drift. Runtime signals include correct sysfs attribute names, accurate ATID bit placement, SYNCR mask behavior, and per-port size programming for supported element widths.
