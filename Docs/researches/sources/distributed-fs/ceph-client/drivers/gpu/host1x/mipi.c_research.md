<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/mipi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/mipi.c

## Purpose

`mipi.c` implements the Tegra MIPI calibration provider/client helper API. It lets CSI/DSI consumers request a calibration device by devicetree phandle and call provider-supplied enable, disable, start, and finish operations.

## Important APIs, Types, And Functions

- `tegra_mipi_enable()`, `tegra_mipi_disable()`, `tegra_mipi_start_calibration()`, and `tegra_mipi_finish_calibration()` call optional provider ops and default to success.
- `tegra_mipi_request()` parses `nvidia,mipi-calibrate`, verifies it matches the singleton provider, obtains the provider platform device, stores ops and pad mask, and returns a handle.
- `tegra_mipi_free()` drops the platform-device reference and frees the handle.
- `devm_tegra_mipi_add_provider()` registers the singleton provider and removes it through a devm action.

## Control Flow

Provider registration stores a device node and ops if no provider exists. Consumers parse a phandle with `#nvidia,mipi-calibrate-cells`, require the parsed node to be the current provider, allocate a `tegra_mipi_device`, and hold a platform-device reference. Operation calls are thin optional callbacks into the provider.

## State And Persistence Behavior

The file stores one global provider `{np, ops}`. Each requested MIPI device stores the provider platform device, ops pointer, and pad selection. Provider state persists until the devm cleanup action clears it.

## Dependencies And Integration Points

Depends on OF phandle parsing, platform devices, and public `<linux/tegra-mipi-cal.h>`. It is registered from `dev.c` as a companion platform driver and used by display/camera drivers needing lane calibration.

## Risks And Test Signals

Only one provider is supported; a second returns `-EBUSY`. Provider matching is by node pointer, so DT must reference the exact provider. Tests should cover missing phandle, wrong provider, provider removal cleanup, request/free reference balance, and providers with partial operation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/mipi.c -->
