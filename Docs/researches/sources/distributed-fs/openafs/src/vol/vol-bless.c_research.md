# sources/distributed-fs/openafs/src/vol/vol-bless.c

## Purpose

`vol-bless.c` is a small command-line utility for setting or clearing a volume's blessed bit. The blessed bit is stored in the volume disk data and affects whether the fileserver considers the volume usable after operations such as salvage or restore.

## Important APIs and Functions

`main` defines command syntax with `-id`, `-bless`, `-unbless`, and `-nofssync`. `handleit` parses options, initializes the volume package with `VInitVolumePackage2`, attaches the requested volume for update with `VAttachVolume(..., V_VOLUPD)`, changes `V_blessed(vp)`, writes the header with `VUpdateVolume`, and detaches with `VDetachVolume`.

`VolumeChanged` is defined as a global to satisfy lower-level physio expectations.

## Control Flow and State

The tool rejects simultaneous `-bless` and `-unbless`. With normal operation it runs as `volumeUtility` and may use FSSYNC to coordinate with a running fileserver. With `-nofssync`, it initializes as `salvager` and disables FSSYNC use. The only intended persistent mutation is the blessed flag in the attached volume header, committed through `VUpdateVolume`.

## Dependencies and Integration Points

The utility depends on OpenAFS command parsing (`afs/cmd.h`), rx/xdr and queue headers, vnode/volume package APIs, and the volume package's FSSYNC option handling. It integrates administratively with fileserver/salvager workflows.

## Risks and Test Signals

Risks are direct metadata mutation on the wrong volume, unsafe `-nofssync` use while a fileserver is active, and failure paths that exit after attach errors. Tests should cover argument validation, bless/unbless persistence, FSSYNC-enabled and no-FSSYNC initialization, failure to attach, failure to update, and idempotent repeated bless/unbless operations on a test volume.
