# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_public.h` is the public CSS stream API and input configuration contract in the Intel AtomISP CSS driver. It defines input modes, MIPI buffer config, ISYS stream configs, `struct ia_css_stream_config`, stream info, and APIs to create/destroy/start/stop streams, manage continuous capture, query formats, and inject FIFO test frames.

## Important APIs, Types, and Functions

Visible functions: `ia_css_stream_create`, `ia_css_stream_get_info`, `ia_css_stream_set_output_padded_width`, `ia_css_stream_get_max_buffer_depth`, `ia_css_stream_capture`, `ia_css_stream_capture_frame`, `ia_css_stream_send_input_frame`, `ia_css_stream_send_input_line`, `ia_css_stream_send_input_embedded_line`, `ia_css_stream_set_isp_config_on_pipe`. Visible structs: `struct ia_css_mipi_buffer_config`, `struct ia_css_stream_isys_stream_config`, `struct ia_css_resolution  input_res; /** Resolution of input data */`, `struct ia_css_stream_input_config`, `struct ia_css_resolution  input_res; /** Resolution of input data */`, `struct ia_css_resolution  effective_res; /** Resolution of input data.`, `struct ia_css_stream_config`, `struct ia_css_input_port  port; /** Port, for sensor only. */`, `struct ia_css_prbs_config prbs; /** PRBS configuration */`, `struct ia_css_stream_isys_stream_config`. Visible enums: `enum ia_css_input_mode`, `enum`, `enum atomisp_input_format format; /** Format of input stream. This data`, `enum atomisp_input_format format; /** Format of input stream. This data`, `enum ia_css_bayer_order bayer_order; /** Bayer order for RAW streams */`, `enum ia_css_input_mode    mode; /** Input mode */`, `enum atomisp_input_format`, `enum atomisp_input_format format,`. Important macros/constants: `__IA_CSS_STREAM_PUBLIC_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The common flow is default config, fill sensor/FIFO/TPG/PRBS/memory input details, create a stream from one or more pipes, start it, queue pipe buffers, capture or stop as needed, then destroy/unload.

## State and Persistence Behavior

State persists in the stream object and firmware queues. Continuous capture settings drive raw buffer allocation/depth, metadata layout, and raw buffer locking.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include invalid channel ids, inconsistent effective/input resolutions, continuous buffer depth underallocation, and using test FIFO injection APIs with mismatched format/two-PPC values.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 553 lines, 19917 bytes.
