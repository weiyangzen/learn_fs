# sources/distributed-fs/ceph-client/drivers/hid/hid-thrustmaster.c

Purpose: initializes Thrustmaster wheels that enumerate as the generic USB HID `Thrustmaster FFB Wheel`. The driver identifies the real wheel model with a vendor control read and sends the model-specific control request that switches the wheel into its full-capability mode.

Important APIs, types, and functions: `struct tm_wheel_info` maps model IDs to switch values and names; `struct tm_wheel_response` describes the vendor response packet; `struct tm_wheel` owns the USB device, one URB, two copied `usb_ctrlrequest` objects, and the model response buffer. `thrustmaster_probe()` parses and starts HID without FF, allocates state, sends safety interrupt packets through `thrustmaster_interrupts()`, then submits a control URB. `thrustmaster_model_handler()` decodes packet type `0x49` or `0x47`, chooses a `tm_wheel_info`, fills `change_request->wValue`, and reuses the URB for the switch request. `thrustmaster_change_handler()` treats normal completion and some protocol failures as likely success because the wheel disconnects/re-enumerates.

Control flow: probe rejects non-USB HID devices, starts HID, allocates all request/response resources, performs the T300RS interrupt prelude, submits a model request, then returns while completion handlers drive the mode switch asynchronously. Remove kills the URB, frees all heap-owned state, and stops HID hardware.

State and persistence: no persistent configuration is stored. Runtime state is the `tm_wheel` drvdata and an in-flight URB; successful mode switching likely causes device reset/re-enumeration. The setup packet arrays and known model table are static constants.

Dependencies and integration: depends on HID core, USB control/interrupt messaging, `hid_is_usb()`, `hid_hw_start()`, and kernel allocation helpers. It registers one USB VID/PID in a `hid_driver` named `hid-thrustmaster`.

Risks: asynchronous URB reuse makes lifetime handling critical; remove must kill the URB before freeing request buffers. Model parsing is based on reverse-engineered packet shapes, and unknown model IDs fail closed. Endpoint assumptions in `thrustmaster_interrupts()` are guarded but still device-specific. Force feedback is deliberately not connected during initial generic HID startup.

Test signals: no KUnit tests. Useful validation is hardware-driven: connect supported wheels, confirm the model log, observe re-enumeration/full mode, and check that removal during an in-flight request does not fault.
