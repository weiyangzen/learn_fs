<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/check.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/check.go

- Purpose: CLI command for running store integrity checks and optional repair.
- Important behavior: Builds `storage.CheckOptions`, invokes `m.Check`, prints layer/image/container problems, and optionally invokes repair options.
- Control flow: Parse flags for scope/repair behavior, call store check, format grouped errors, and set nonzero exit when problems or repair failures are present.
- State and persistence: Read-only unless repair is requested, in which case store contents may be deleted through library repair.
- Dependencies and integration: Calls the exported storage `Check`/`Repair` APIs and uses the common command registry in `main.go`.
- Risks: Repair is destructive; output format is intended for humans and may not be stable for scripts.
- Test signals: CLI integration tests and library check tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/check.go -->
