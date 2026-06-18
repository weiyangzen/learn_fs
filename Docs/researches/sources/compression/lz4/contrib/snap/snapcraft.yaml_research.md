# sources/compression/lz4/contrib/snap/snapcraft.yaml

## Purpose
This Snapcraft manifest packages the LZ4 command-line application as a strict, stable snap named `lz4`.

## Important Fields
Top-level metadata includes `name: lz4`, `version: 1.9.4`, a compression-focused summary and long description, `confinement: strict`, `grade: stable`, and `base: core20`. The `apps.lz4` command is `usr/local/bin/lz4` with the `home` plug. The single part `lz4` uses `source: ../` and the `make` plugin.

## Control Flow
Snapcraft reads the manifest, pulls the parent source tree, builds it with the make plugin, and exposes the installed `lz4` binary as the snap command.

## State and Persistence
No runtime state is defined here. Build output and installed files are managed by Snapcraft. The version is hard-coded rather than extracted from `lz4.h`.

## Dependencies and Integration Points
It integrates with Snapcraft and the repository's make-based install behavior. The strict confinement and `home` plug decide user-visible filesystem access for the packaged CLI.

## Risks
The hard-coded `1.9.4` version can drift from the repository version. `source: ../` is relative to `contrib/snap`, so moving the manifest or invoking it from unexpected layouts can change build context. Strict confinement may block workflows that expect arbitrary filesystem access outside home unless additional plugs are added.

## Test Signals
Build with Snapcraft, inspect the resulting snap metadata, run `lz4 --version` inside the snap, and test compression/decompression on files under `$HOME`.
