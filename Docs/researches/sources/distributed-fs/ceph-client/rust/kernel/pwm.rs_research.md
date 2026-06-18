# sources/distributed-fs/ceph-client/rust/kernel/pwm.rs

## Purpose
Provides Rust abstractions for PWM devices and chips, including waveform conversion, consumer-side waveform operations, driver operation callbacks, vtable generation, chip allocation, registration, refcounting, and platform-driver module glue.

## APIs, Types, and Functions
`Waveform` mirrors `struct pwm_waveform`; `RoundingOutcome` reports whether rounding was exact/down or up; `Device` wraps `pwm_device` and exposes `hwpwm`, `chip`, `label`, `set_waveform`, `round_waveform`, and `get_waveform`. `PwmOps` defines driver hooks for request, capture, waveform round-trip conversion, hardware read, and hardware write with associated `WfHw`. `RoundedWaveform<WfHw>` carries callback status and hardware form. `Adapter<T>` serializes/deserializes hardware waveforms, bridges C callbacks, and installs a release callback. `PwmOpsVTable`, `create_pwm_ops`, `Chip<T>`, `UnregisteredChip`, `Registration`, and `module_pwm_platform_driver!` cover controller registration and cleanup.

## Control Flow, State, and Persistence
Consumer methods convert between Rust and C waveforms and call `*_might_sleep` PWM helpers. Driver registration allocates a `pwm_chip` plus private data, pinned-initializes `T` in the private area, installs a release callback and static ops table, wraps the chip in `ARef`, and returns an `UnregisteredChip`. `register` calls `__pwmchip_add`, then devres-registers a `Registration` guard whose drop calls `pwmchip_remove`. Final device release drops the Rust driver data and delegates to `pwmchip_release`. Refcounting is implemented via the chip's embedded `struct device`.

## Dependencies and Integration
Depends on PWM generated bindings, `device`, `devres`, `ARef`, `AlwaysRefCounted`, `container_of`, `PinInit`, and platform-driver macros. It integrates with the C PWM core, parent bound devices, devres cleanup, and the `PWM` namespace import through `module_pwm_platform_driver!`.

## Risks and Test Signals
Risks include `WfHw` size exceeding `PWM_WFHWSIZE`, incorrect serialization of non-plain-old-data hardware representations, callback assumptions that parent devices are bound, cleanup gaps if devres registration fails after `__pwmchip_add`, and double-drop risks around custom release handling. Test signals include chip allocation failure injection, `WfHw` size compile checks, callback error propagation tests, register/drop cleanup tests, waveform round-trip tests, and namespace/module build checks.
