# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_platform.h

## Purpose
This header defines AtomISP platform-facing camera topology, CSI input formats, sensor platform callbacks, MIPI metadata, and SoC detection helpers. It is the common contract between AtomISP core, sensor drivers, and board/G-Min platform glue.

## Important APIs, Types, And Data
- `enum atomisp_bayer_order` describes raw Bayer ordering.
- `enum atomisp_input_stream_id` and `enum atomisp_input_format` describe CSI streams and MIPI data formats, including RAW, YUV, RGB, embedded, generic short packets, and user-defined data.
- `struct intel_v4l2_subdev_table` maps camera ports and lane counts to V4L2 subdevs.
- `struct atomisp_isys_config_info` and `struct atomisp_input_stream_info` describe per-stream input-system configuration and virtual-channel data.
- `struct camera_sensor_platform_data` provides callbacks for FLIS clock, CSI setup, GPIO lines, and voltage rails (`v1p8`, `v2p8`, `v1p2`).
- `struct camera_mipi_info` records port, lane count, input format, Bayer order, and metadata format/size/effective width.
- `atomisp_platform_get_subdevs()`, `atomisp_register_sensor_no_gmin()`, and `atomisp_unregister_subdev()` expose platform registration/enumeration.
- SoC macros identify Medfield, Bay Trail, Cherry Trail, Merrifield, Moorefield, and ISP2401-capable SoCs from `boot_cpu_data.x86_vfm`.

## Control Flow
Platform code registers or enumerates sensor subdevs with port/lane/format metadata. Sensor drivers receive `camera_sensor_platform_data`, use callbacks to power and route hardware, and pass `camera_mipi_info` to the host through V4L2 subdev host data. AtomISP core uses SoC macros and topology data to select hardware-specific configuration.

## State And Persistence
The header owns no state. Runtime state is held in platform tables, subdev host data, and callback implementations. The callback interface controls hardware state for clocks, regulators, GPIOs, and CSI routing.

## Dependencies And Integration Points
It depends on x86 CPU identification, Linux I2C, V4L2 subdevs, and `atomisp.h`. It integrates with sensor probe/configuration, AtomISP PCI core, G-Min helpers, and non-G-Min platform registration paths.

## Risks
- Callback pointers are optional by type but often assumed present by drivers; inconsistent validation can crash during power sequencing.
- `ATOMISP_INPUT_STREAM_GENERAL` and `ATOMISP_INPUT_STREAM_CAPTURE` both equal zero, which is intentional aliasing but can confuse generic code.
- SoC macros rely on `boot_cpu_data.x86_vfm`; portability outside intended Intel Atom platforms is limited.
- `metadata_effective_width` is a pointer, so ownership/lifetime must be clear when attached as host data.

## Test Signals
Validation should cover sensor registration/enumeration for G-Min and no-G-Min paths, correct port/lane/format propagation to CSI configuration, callback failure rollback in sensor drivers, SoC macro behavior on supported CPU IDs, and multi-stream virtual-channel configuration with embedded metadata.
