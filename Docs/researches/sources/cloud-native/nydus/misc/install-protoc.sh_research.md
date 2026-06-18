<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/install-protoc.sh -->
# sources/cloud-native/nydus/misc/install-protoc.sh

## Purpose

This script installs a pinned protobuf compiler release for supported OS/architecture combinations.

## Important APIs, Types, and Functions

It uses `set -euo pipefail`, `PROTOC_VERSION=29.6`, auto-detects system (`linux` or `osx`) and architecture (`amd64`, `arm64`, `ppc64le`, `riscv64`), maps to protobuf release archive names, downloads with `curl`, unzips to `/usr/local` with sudo, and removes the zip.

## Control Flow

Optional command-line arguments override architecture and system. Unsupported OS/arch exit non-zero, while riscv64 exits zero after printing a skip message because upstream protoc archive is unsupported.

## State and Persistence Behavior

It writes a downloaded zip in the current directory, installs files under `/usr/local`, and removes the zip afterward.

## Dependencies and Integration Points

It depends on curl, sudo, unzip, uname, and GitHub protobuf releases. `misc/prepare.sh` calls it during performance environment setup.

## Risks and Test Signals

The script trusts the downloaded archive without checksum verification and requires sudo. Network or GitHub availability affects reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/install-protoc.sh -->
