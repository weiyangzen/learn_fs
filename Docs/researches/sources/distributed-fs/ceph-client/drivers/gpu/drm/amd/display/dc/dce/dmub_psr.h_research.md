# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.h

Purpose: declares the DMUB PSR object and function table used by DC code to control Panel Self Refresh through firmware.

Important types and APIs: `struct dmub_psr` stores `struct dc_context *ctx` and `const struct dmub_psr_funcs *funcs`. The function table covers settings copy, enable/disable with optional wait, state query, level, force-static, residency, sink vtotal in active PSR, and power options. Factory/destructor functions are `dmub_psr_create()` and `dmub_psr_destroy()`.

Control flow role: callers allocate the object, then use `funcs` to send PSR commands without depending on implementation details. Settings-copy is the setup gate before enable; state/residency queries provide firmware feedback.

State and persistence: the object is lightweight; firmware stores PSR state and copied hardware context. Caller-owned link and PSR context inputs must remain valid through command construction.

Dependencies and integration: includes `dc_types.h` and `dmub_cmd.h`, and forward-declares `struct dc_link`. It integrates with link power management, PSR policy, and hardware lock paths.

Risks and test signals: API users must handle `dmub_psr_create()` returning null and must not call function pointers after destroy. Versioned command structures in `dmub_cmd.h` must remain compatible. Test signals include compile compatibility with PSR enums and residency modes, lifecycle, settings-copy before enable, and wait/no-wait enable behavior.
