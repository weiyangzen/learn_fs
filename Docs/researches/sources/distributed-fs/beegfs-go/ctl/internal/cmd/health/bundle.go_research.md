
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/bundle.go

- Purpose: creates `health bundle <path>` support archives containing CTL command output.
- Important APIs: `supportFile`, `supportCommand`, `supportBundleContents`, `newBundleCmd`, `getGlobalConfig`, `collectSupportFiles`, `bundleSupportFiles`, and `addFileToTar`.
- Control flow/state: creates timestamped temp directory, runs configured subcommands with global flags and forced debug, writes sectioned text files, tars/gzips them, and deletes the temp directory.
- Dependencies/integration: uses Viper settings, `os.Args[0]` self-exec, tar/gzip writers, and health utility headers.
- Risks/tests: temporarily reassigns global `os.Stdout`/`os.Stderr`; command failures are embedded and ignored per section. Bundle filename uses RFC3339 colons. No direct tests found.
