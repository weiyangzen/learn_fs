# sources/cloud-native/moby/contrib/dockerize-disk.sh

## Purpose
Converts a disk image into a Docker image layer set, optionally diffing against a base image.

## APIs, Types, And Functions
The shell functions are `usage` and `cleanup`. The script depends on `qemu-nbd`, kernel `nbd`, `mount`, `aufs`, Docker CLI operations, `tar`, `diff`, and shell processing of add/update/delete entries.

## Control Flow, State, And Integration
The script parses image name/tag, attaches the disk image read-only via NBD, mounts it, optionally unpacks base image layers, mounts an AUFS workdir, diffs disk and workdir contents, and builds Docker image metadata/layers. Cleanup unmounts and detaches NBD on exit.

## Risks And Test Signals
Risks are high because it requires root, NBD devices, AUFS, and destructive mount cleanup. Integration is with legacy image-format assembly and host kernel storage drivers; failures can leave mounts or NBD devices attached.
