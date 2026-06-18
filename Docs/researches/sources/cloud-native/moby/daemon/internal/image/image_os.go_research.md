## sources/cloud-native/moby/daemon/internal/image/image_os.go

Purpose: Validates that an image operating system matches the daemon host OS.

Important API: `CheckOS(os string) error` compares the supplied OS to `runtime.GOOS` case-insensitively and returns `errdefs.InvalidParameter` on mismatch.

Control flow and state: A single string comparison with no persistent state.

Dependencies and integration: Used by image store restore/create and tar export save/load to reject unsupported platform images before retaining layers or importing configs.

Risks: Empty OS does not match any normal runtime GOOS; other code often defaults missing OS through `Image.OperatingSystem`, so direct callers must pass the normalized value. The error message is intentionally generic.

Tests: No dedicated tests in this subset; coverage is indirect through image store and tar export paths.
