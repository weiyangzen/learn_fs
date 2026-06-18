# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ini.h

## Purpose
`ini.h` defines the wl1271/wl128x NVS/INI binary layouts for platform and RF calibration data. These structures describe clocks, SmartReflex, 2.4 GHz and 5 GHz static radio parameters, FEM-specific dynamic power tables, RSSI compensation, trace loss, and NVS section sizes.

## Important APIs and types
Key types include `wl1271_ini_general_params`, `wl128x_ini_general_params`, band parameter structures for 2.4 GHz and 5 GHz, FEM parameter structures for wl1271 and wl128x, `wl1271_nvs_file`, and `wl128x_nvs_file`. Constants define channel/sub-band/rate-group counts, FEM module mapping, the NVS section size, and the legacy NVS file size.

## Control flow and integration
The header has no executable flow. Loader/calibration code interprets firmware/NVS blobs using these packed structures and may map four logical FEM module types into two stored NVS entries via `WL12XX_FEM_TO_NVS_ENTRY()`.

## State and persistence behavior
This is persistent board calibration data. The NVS section must be first in both top-level file structures, followed by the INI section. Layout, count constants, and padding bytes are part of the on-disk/on-flash ABI.

## Dependencies and risks
The structures depend on exact packing and little-endian fields for voltage values. Risks include using a wl1271 layout for wl128x data, wrong FEM mapping, malformed calibration blobs, and array-size/count drift corrupting subsequent fields.

## Test signals
Signals include successful NVS loading, clock/ref-clock configuration, sane per-band power limits, valid FEM selection, calibration test command results, and RF behavior across channels and temperature/power states.
