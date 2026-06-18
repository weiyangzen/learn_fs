
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/flags.go

- Purpose: supplies custom `pflag.Value` implementations for entry create/set configuration.
- Important APIs: `chunksizeFlag`, `poolFlag`, `stripePatternFlag`, `numTargetsFlag`, `rstCooldownFlag`, `accessControlFlag`, `dataStateFlag`, `permissionsFlag`, `userFlag`, and `groupFlag`.
- Control flow/state: parsers set pointer fields in backend configs to distinguish unchanged values from explicit values; UID/GID and permissions constructors also install defaults.
- Dependencies/integration: uses `util.ParseIntFromStr`, BeeGFS entity and enum types, OS effective UID/GID, and duration parsing.
- Risks/tests: pointer-to-pointer state is subtle; `rstCooldownFlag` does not reject negative durations, and permission parsing does not bound mode bits. No direct tests in this file.
