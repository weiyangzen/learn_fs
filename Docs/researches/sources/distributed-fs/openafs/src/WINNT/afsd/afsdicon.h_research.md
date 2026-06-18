# sources/distributed-fs/openafs/src/WINNT/afsd/afsdicon.h

## Purpose

`afsdicon.h` is a minimal resource/menu identifier header for the Windows AFSD icon or UI resources. It currently defines a help command identifier.

## Important APIs, Types, and Functions

- Include guard `OPENAFS_WINNT_AFSD_AFSDICON_H`.
- `IDM_HELP` is defined as `100`.

## Control Flow

There is no executable control flow. Resource scripts or UI code include this header to keep numeric command IDs consistent.

## State and Persistence Behavior

The header has no runtime state and no persistence behavior.

## Dependencies and Integration Points

It integrates with Windows resource compilation and any tray/icon/menu code that handles `IDM_HELP`.

## Risks

- Numeric resource IDs must remain unique across the resource set; this file alone does not show collisions.
- Removing or renumbering `IDM_HELP` can break resource scripts or command handlers.

## Test Signals

- Resource build tests should verify this header is included successfully and no duplicate resource ID warnings occur.
- UI smoke tests should verify the help command still maps to the intended handler.
