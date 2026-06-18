# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe_public.h` is the public CSS pipe API and configuration contract in the Intel AtomISP CSS driver. It exposes pipe modes, pipe versions, `struct ia_css_pipe_config`, `struct ia_css_pipe_info`, and APIs to create/destroy pipes, query info, set ISP config, manage event IRQ masks, enqueue/dequeue buffers, set scaler LUTs, and override output formats.

## Important APIs, Types, and Functions

Visible functions: `ia_css_pipe_create`, `ia_css_pipe_get_info`, `ia_css_pipe_set_isp_config`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_event_get_irq_mask`. Visible structs: `struct ia_css_pipe_config`, `struct ia_css_resolution input_effective_res;`, `struct ia_css_resolution bayer_ds_out_res;`, `struct ia_css_resolution capt_pp_in_res;`, `struct ia_css_resolution vf_pp_in_res;`, `struct ia_css_resolution output_system_in_res;`, `struct ia_css_resolution dvs_crop_out_res;`, `struct ia_css_frame_info output_info[IA_CSS_PIPE_MAX_OUTPUT_STAGE];`, `struct ia_css_frame_info vf_output_info[IA_CSS_PIPE_MAX_OUTPUT_STAGE];`, `struct ia_css_capture_config default_capture_config;`. Visible enums: `enum`, `enum ia_css_pipe_mode`, `enum ia_css_pipe_version`, `enum ia_css_pipe_mode mode;`, `enum ia_css_pipe_version isp_pipe_version;`, `enum ia_css_frame_delay dvs_frame_delay;`, `enum ia_css_frame_format format);`. Important macros/constants: `__IA_CSS_PIPE_PUBLIC_H`, `IA_CSS_PIPE_MODE_NUM`, `DEFAULT_PIPE_CONFIG`, `DEFAULT_PIPE_INFO`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The typical flow is defaults, fill mode/resolutions/output formats, create pipe, attach to a stream, optionally set ISP/filter config or IRQ masks, then queue/dequeue buffers while streaming.

## State and Persistence Behavior

Pipe state persists in the created pipe object and in firmware/SP queues after stream start. Some config pointers are copied, while table pointers such as shading/morph are not deeply copied according to `ia_css_types.h`.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include invalid resolution combinations, calling override/scaler APIs after stream start, mismatched output pin indexes, and buffer ownership mistakes after enqueue.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 464 lines, 17399 bytes.
