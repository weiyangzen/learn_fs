
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/copy/copy.go

- Purpose: exposes licensed parallel copy functionality as `copy`/`cp`, wrapping `/opt/beegfs/sbin/beegfs-copy`.
- Important APIs: `NewCopyCmd`, `frontendCfg`, `copyRunner`, `copyUsingStdin`, and `readBatchFromStdin`.
- Control flow/state: validates binary presence, verifies license feature `io.beegfs.copy`, translates Go flags via `bflag`, runs the external copy binary, and optionally batches stdin paths by delimiter and batch size.
- Dependencies/integration: uses `config.ManagementClient`, `VerifyLicense`, `bflag`, stdin utilities, `os/exec`, and logger debug fields.
- Risks/tests: `copyRunner` calls `os.Exit` on external nonzero exit, bypassing normal Cobra cleanup; `copyUsingStdin` does not return errors from `copyRunner`, so batched failures can be lost. No direct tests found.
