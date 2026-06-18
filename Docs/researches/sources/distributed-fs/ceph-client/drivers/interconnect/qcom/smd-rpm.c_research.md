# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/smd-rpm.c

## Purpose

`smd-rpm.c` is a small communication wrapper that lets legacy Qualcomm interconnect drivers send bandwidth and bus-clock votes to the Resource Power Manager over SMD. It is separate from the RPMh path used by the SM8250 and newer files above; this wrapper supports older RPM/SMD-based interconnect providers.

## Important APIs, Types, and Functions

The file defines a single global `static struct qcom_smd_rpm *icc_smd_rpm` and exports three GPL symbols. `qcom_icc_rpm_smd_available()` returns whether the RPM handle has been discovered. `qcom_icc_rpm_smd_send(int ctx, int rsc_type, int id, u32 val)` builds an `icc_rpm_smd_req` with key `RPM_KEY_BW`, a 32-bit payload size, and the requested value, then calls `qcom_rpm_smd_write()`. `qcom_icc_rpm_set_bus_rate(const struct rpm_clk_resource *clk, int ctx, u32 rate)` builds a `clk_smd_rpm_req` using `QCOM_RPM_SMD_KEY_RATE`; branch clocks are normalized to boolean on/off before writing.

## Control Flow

The platform driver is named `icc_smd_rpm` and is registered with `module_platform_driver`. Probe obtains the parent RPM handle with `dev_get_drvdata(pdev->dev.parent)` and stores it in the global. If the handle is missing, probe logs an error and returns `-ENODEV`. Remove clears the global pointer. Exported send functions are then called by RPM interconnect code when aggregating bus bandwidth or clock-rate changes.

## State and Persistence

State is intentionally minimal and global. The RPM handle persists in `icc_smd_rpm` only while the wrapper platform device is bound. There is no reference counting, locking, queueing, or cached vote state in this file; callers are expected to use it only after availability is true and while the device remains registered. Request structs are stack-local and serialized immediately through `qcom_rpm_smd_write`.

## Dependencies and Integration Points

The wrapper depends on `linux/soc/qcom/smd-rpm.h`, `icc-rpm.h`, platform-device infrastructure, and the parent Qualcomm SMD RPM device. It integrates with older Qualcomm interconnect providers that call the exported symbols to send RPM bus master/slave requests or bus clock rate requests. The request format must match RPM firmware expectations: little-endian key, byte count, and value.

## Risks

The global pointer has no internal locking, so correctness depends on normal platform-device lifetime and module dependencies preventing calls after remove. Calling `qcom_icc_rpm_smd_send` before successful probe would pass a null RPM handle to `qcom_rpm_smd_write`. Branch clock coercion is intentional but easy to misuse if a non-branch clock is described incorrectly. Endianness and key constants are firmware ABI details and should not be changed casually.

## Test Signals

Probe should succeed only when the parent SMD RPM driver has provided drvdata. Legacy interconnect clients should see successful RPM writes for bandwidth and bus-rate updates, with no `unable to retrieve handle to RPM` log. Useful tests include booting an RPM/SMD platform, exercising interconnect bandwidth requests, toggling branch-clock resources, and verifying no calls occur before `qcom_icc_rpm_smd_available()` returns true.
