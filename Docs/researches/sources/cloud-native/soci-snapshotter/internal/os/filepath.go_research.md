# sources/cloud-native/soci-snapshotter/internal/os/filepath.go

Purpose: validates executable paths before using them as external command binaries, reducing command-injection and misconfiguration risk for decompression streams.

Important APIs/types/functions: `SanitizeExecutablePath` returns a resolved executable path or an error. Sentinel errors include `errFilePathContainsInvalidCharacters`, `errFilePathIsADirectory`, and `errFilePathIsNotExecutable`.

Control flow: validation rejects paths containing `#%{}\|;&$<>`, cleans the path, resolves symlinks, computes an absolute path for stat checks, rejects directories, verifies any executable bit is set, and returns the symlink-resolved path.

State and persistence: no persistent state; reads filesystem metadata and symlink targets.

Dependencies/integration points: used by `internal/archive/compression.InitializeDecompressStreams` before spawning configured decompressor binaries.

Risks: the returned value is `resolvedPath`, not the absolute path, so relative input can produce a relative resolved path even though stat was checked through `absPath`. Character filtering is conservative but not a complete policy for all OS/path edge cases. It validates the binary path only, not its arguments.

Test signals: tests cover valid executable, symlink resolution, invalid characters, nonexistent path, broken symlink, directory, and non-executable file.
