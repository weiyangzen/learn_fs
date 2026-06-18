# sources/cloud-native/containerd/cmd/ctr/commands/images/convert.go

Purpose: implements `ctr images convert`, creating a new image reference with transformed layer/media formats.

Important APIs/functions: `convertCommand`; converter options for platform selection, uncompressing layers, Docker-to-OCI media conversion, and EROFS layer conversion.

Control flow: validates source and target refs, selects default strict platform unless `--all-platforms` or explicit platforms are supplied, appends layer conversion functions for `--uncompress` and/or `--erofs`, validates EROFS mode `raw|zstd`, parses EROFS compressors and mkfs options, optionally enables Docker-to-OCI conversion, creates client/context, runs `converter.Convert()`, and prints the new target digest.

State and persistence: writes converted content and image metadata under the target reference.

Dependencies/integration: containerd image converter packages, EROFS converter, uncompress converter, platform parsing, shared client helper.

Risks: conversion options can be combined and order matters in the option list. `strings.Fields` for mkfs options does not support shell-like quoting. All-platforms conversion requires all referenced content to already exist.

Test signals: no local tests in this subset.
