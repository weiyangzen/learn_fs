# sources/distributed-fs/ceph-client/include/soc/qcom/rpmh.h

Purpose: declares the public Qualcomm RPMh write API for sending TCS command arrays to the Resource Power Manager hardware accelerator.

Important APIs/types/functions: when `CONFIG_QCOM_RPMH` is enabled, exports `rpmh_write`, `rpmh_write_async`, `rpmh_write_batch`, and `rpmh_invalidate`; disabled builds return `-ENODEV` or no-op invalidate. The API consumes `enum rpmh_state` and `struct tcs_cmd` from `soc/qcom/tcs.h`.

Control flow: clients build one or more TCS commands, choose sleep, wake-only, or active-only state, then issue synchronous, asynchronous, or batch writes. `rpmh_invalidate()` clears cached/aggregated state for a device.

State and persistence: RPMh implementation maintains request aggregation and state caches; hardware stores active/sleep/wake votes in TCS/RSC resources. This header has no state.

Dependencies and integration: depends on `soc/qcom/tcs.h` and `linux/platform_device.h`. Consumers include RPMh regulators, clocks, power domains, interconnect BCM voting, and SoC drivers.

Risks: wrong state selection or command count can leave resources underpowered, overpowered, or stuck across suspend. Async writes have different completion semantics than sync writes. Test signals include RPMh regulator/clock/interconnect probe, suspend/resume, command timeout handling, and disabled-config builds.
