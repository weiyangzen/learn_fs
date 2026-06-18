# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream.h` is the private CSS stream runtime state definition in the Intel AtomISP CSS driver. It defines `struct ia_css_stream`, storing public stream config/info, RX configuration, pipe list, continuous-pipe pointers, ISP parameter caches, continuous capture flags, stop/start state, and testing/helper APIs.

## Important APIs, Types, and Functions

Visible functions: `sh_css_params_set_binning_factor`, `ia_css_get_isp_dis_coefficients`, `ia_css_get_isp_dvs2_coefficients`. Visible structs: `struct ia_css_stream`, `struct ia_css_stream_config    config;`, `struct ia_css_stream_info      info;`, `struct ia_css_pipe            *last_pipe;`, `struct ia_css_pipe           **pipes;`, `struct ia_css_pipe            *continuous_pipe;`, `struct ia_css_isp_parameters  *isp_params_configs;`, `struct ia_css_isp_parameters  *per_frame_isp_params_configs;`, `struct ia_css_binary *`, `struct ia_css_binary *`. Visible enums: none visible in this file. Important macros/constants: `_IA_CSS_STREAM_H_`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Public stream creation fills this private object, links pipes, computes RX/input settings, initializes ISP parameter caches, and later start/stop updates firmware/SP pipeline state.

## State and Persistence Behavior

State persists for the stream lifetime and includes per-frame ISP parameter caches and continuous capture flags that affect raw buffer management.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include stale `last_pipe`, mismatched `num_pipes` and `pipes`, parameter cache invalidation errors, and stop/start state races.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 99 lines, 2823 bytes.
