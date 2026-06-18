# sources/compression/zstd/contrib/snap/snapcraft.yaml

Purpose: Snapcraft packaging manifest for building a development-mode `zstd` snap exposing the `zstd`, `zstdgrep`, and `zstdless` commands from a make-based build.

Important fields: package `name: zstd`, `version: git`, summary/description, `grade: devel`, `confinement: devmode`, app commands under `usr/local/bin`, plugs `home` and `removable-media`, and a single `parts.zstd` using `source: .`, `plugin: make`, and `build-packages: [g++]`.

Control flow: Snapcraft fetches/uses the current tree as the part source, runs the make plugin, installs the resulting artifacts, and maps three commands as snap apps. Runtime file access is controlled by the listed plugs and devmode confinement.

State and persistence: build artifacts are managed by Snapcraft. The manifest itself carries no runtime persistence; installed commands read/write user files according to snap interfaces.

Dependencies/integration: integrates with Snapcraft's make plugin and assumes the upstream zstd Makefile installs into `usr/local/bin` inside the snap staging area. It depends on a C++ compiler package even though much of zstd is C, likely for build/test compatibility.

Risks: `grade: devel` and `confinement: devmode` are unsuitable for stable channel publication. The manifest does not pin a base, architectures, or install target details. Missing plugs could affect strict confinement later, while broad removable-media access may be too permissive.

Test signals: `snapcraft` should produce a snap containing all three commands; install with devmode and run compression/decompression on home and removable-media paths; strict-confinement migration should test interfaces explicitly.
