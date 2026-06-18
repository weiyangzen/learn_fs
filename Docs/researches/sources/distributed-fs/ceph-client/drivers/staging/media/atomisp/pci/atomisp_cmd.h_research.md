# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.h

## Purpose

`atomisp_cmd.h` is the public internal command header for `atomisp_cmd.c` and related AtomISP PCI driver files. It declares the helper, interrupt, feature-control, parameter-copy, format, sensor, raw-buffer, and power APIs used across the AtomISP staging driver. It also centralizes a few PCI interrupt bit constants used by MSI setup/teardown.

## Important APIs, Types, and Functions

The header forward-declares `struct atomisp_device` and `struct ia_css_frame`, includes the user AtomISP ABI, Linux interrupt/V4L2 headers, local internal driver state, and CSS type headers. It exports helper APIs such as `dump_sp_dmem()`, `atomisp_to_sensor_mipi_info()`, `atomisp_to_video_pipe()`, `atomisp_reset()`, queue flush/completion helpers, IRQ/recovery APIs, format helpers, ISP feature controls, CSS parameter-copy helpers, sensor power/topology helpers, raw exposure APIs, event injection, invalid-frame queries, and power hooks.

Key API groups are:

- PCI/MSI constants: `MSI_ENABLE_BIT`, `INTR_DISABLE_BIT`, `BUS_MASTER_ENABLE`, `MEMORY_SPACE_ENABLE`, `INTR_IER`, and `INTR_IIR`.
- Interrupt and recovery declarations: `atomisp_msi_irq_init()`, `atomisp_msi_irq_uninit()`, `atomisp_assert_recovery_work()`, `atomisp_isr()`, and `atomisp_isr_thread()`.
- Format declarations: `get_atomisp_format_bridge_from_mbus()`, `atomisp_is_mbuscode_raw()`, `atomisp_is_viewfinder_support()`, `atomisp_try_fmt()`, `atomisp_set_fmt()`, `atomisp_get_padding()`, and `atomisp_get_pixel_depth()`.
- Parameter declarations: `atomisp_set_parameters()`, `atomisp_param()`, `atomisp_cp_general_isp_parameters()`, `atomisp_cp_lsc_table()`, `atomisp_css_cp_dvs2_coefs()`, `atomisp_cp_morph_table()`, `atomisp_cp_dvs_6axis_config()`, `atomisp_makeup_css_parameters()`, `atomisp_apply_css_parameters()`, and `atomisp_free_css_parameters()`.
- Sensor/topology declarations: `atomisp_s_sensor_power()`, `atomisp_select_input()`, `atomisp_setup_input_links()`, and `atomisp_port_to_mipi_port()`.
- Buffer and raw-buffer declarations: `atomisp_buf_done()`, `atomisp_handle_parameter_and_buffer()`, `atomisp_flush_params_queue()`, `atomisp_exp_id_unlock()`, `atomisp_exp_id_capture()`, and `atomisp_init_raw_buffer_bitmap()`.

## Control Flow and Integration

This header defines cross-file call boundaries rather than executable control flow. It exposes the commands used by ioctl/control paths, fops/streaming paths, IRQ registration, media graph setup, CSS compatibility layers, and power management. Most APIs take `struct atomisp_sub_device *`, `struct atomisp_device *`, `struct video_device *`, or `struct atomisp_video_pipe *`, making the subdevice/device/pipe split the organizing contract for callers.

The parameter-copy declarations reveal the two-stage parameter flow: user ABI structures are copied into `struct atomisp_css_params`, optional per-frame makeup combines partial parameter sets, then `atomisp_apply_css_parameters()` maps update flags into active CSS configuration. The format declarations show a similar staged flow: try format, set sensor/input topology, configure CSS, and fill V4L2 pix format state.

## State and Persistence Behavior

The header itself has no persisted state and defines no storage except preprocessor constants. Its declarations mutate driver runtime state owned elsewhere: vb2 frame lists, CSS parameter allocations, sensor power state, media links, raw-buffer lock bitmaps, and hardware registers. Because many functions return Linux error codes and operate on pointer-rich user ABI objects, callers must observe the locking and lifetime requirements implemented in `atomisp_cmd.c`.

## Dependencies and Integration Points

`atomisp_cmd.h` depends on `../../include/linux/atomisp.h`, `<linux/interrupt.h>`, `<linux/videodev2.h>`, V4L2 subdev declarations, `atomisp_internal.h`, `ia_css_types.h`, and `ia_css.h`. It is an internal driver header, not a stable external ABI; the userspace structs come from `include/linux/atomisp.h`. It integrates command implementation with AtomISP ioctl/fops/subdev files, CSS wrappers from `atomisp_compat.h`, and power-management functions implemented elsewhere.

## Risks and Edge Cases

- The header is very broad, so unrelated subsystems can easily grow dependencies on command-layer internals.
- Several prototypes expose raw user ABI structures and CSS allocation-bearing structures; wrong callers can leak memory or bypass expected locking.
- Some comments contain outdated behavior hints, so implementation should be treated as authoritative.
- `atomisp_power_off()` and `atomisp_power_on()` are declared here despite not being part of the command implementation body, creating a cross-module dependency that can be easy to miss during refactors.

## Test Signals

Compile coverage is the main signal for this header. Useful additional checks are include dependency review, sparse address-space checking for functions that accept user pointers indirectly, and call-site audits for functions whose implementation asserts `isp->mutex`, pipe `irq_lock`, media graph mutex, or other locks.
