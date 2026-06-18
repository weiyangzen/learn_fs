# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.c

## Purpose
`ipu6-isys.c` is the auxiliary driver for the IPU6 input system. It registers the ISYS media device, V4L2 device, CSI-2 receiver subdevices, capture video nodes, async sensor notifier, runtime PM handlers, firmware message buffers, ISR path, and iWake watermark programming.

## Important APIs, Types, And Functions
Key routines include `isys_probe()`, `isys_remove()`, runtime PM resume/suspend, `isys_register_devices()`, `isys_notifier_init()`, `isys_isr()`, `isys_isr_one()`, `ipu6_get_fw_msg_buf()`, `ipu6_put_fw_msg_buf()`, `ipu6_cleanup_fw_msg_bufs()`, and exported `update_watermark_setting()`. It uses `struct ipu6_isys`, `struct isys_fw_msgs`, `struct isys_iwake_watermark`, and `struct ltr_did`.

## Control Flow
Probe defers until the PCI parent marks the bus ready, allocates ISYS state and CSI-2 receivers, initializes locks/lists/streams, maps firmware in non-secure mode, allocates firmware command buffers, selects the PHY power callback by hardware version, and registers media/V4L2/video/CSI/notifier devices. Firmware message buffers are preallocated and moved between free and firmware-owned lists.

Runtime resume initializes the IPU6 MMU hardware, raises CPU latency QoS, starts TSC sync, marks ISYS powered, programs interrupt registers/CDC thresholds, and sets LTR/DID for ISYS-on. Runtime suspend clears power, resets `need_reset`, drops QoS, restores off LTR/DID, and marks MMU not ready.

The top-level ISR masks non-SW ISYS IRQs while draining CSI and firmware responses. CSI sync IRQs translate FS/FE by virtual channel into SOF/EOF events. Firmware responses complete stream command completions, return firmware message buffers on `PIN_DATA_READY`, complete vb2 buffers, update stream error state, and record SOF timestamps/sequences.

## State And Persistence
State persists only while the auxiliary device is bound. `power` protects ISR access, `need_reset` blocks later opens after firmware/HW cleanup anomalies, `stream_opened` blocks system suspend, and the watermark list tracks active stream data rates. No disk persistence exists.

## Dependencies And Integration Points
The driver integrates the IPU6 auxiliary bus, buttress/TSC, CPD firmware package directory, custom IPU6 DMA/MMU, IPU6 firmware ISYS ABI, media controller, V4L2 async sensor binding, `ipu_bridge` ACPI/fwnode sensor discovery, and CSI-2 PHY implementations.

## Risks And Test Signals
`isys_iwake_watermark_cleanup()` calls `list_del()` on the list head itself, which is unusual and worth static-analysis attention. `isys_remove()` unregisters devices before notifier cleanup, while probe error paths differ; teardown ordering should be stress-tested. Firmware response handling depends on valid stream handles and refcounts. Tests should include probe/remove, async sensor binding with invalid ports, runtime PM cycles, firmware timeouts/errors, CSI receiver error IRQs, suspend while streams are open, and iWake behavior with multiple active streams.
