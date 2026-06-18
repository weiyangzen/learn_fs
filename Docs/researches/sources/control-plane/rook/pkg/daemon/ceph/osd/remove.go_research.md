# sources/control-plane/rook/pkg/daemon/ceph/osd/remove.go

## Purpose
`remove.go` implements OSD removal and replacement cleanup workflows. It validates that requested OSDs are down, marks them out, waits until safe to destroy unless forced, deletes Kubernetes deployments/jobs/PVCs, purges Ceph OSD metadata, optionally removes CRUSH host entries, archives crash warnings, and supports explicit destroy-and-zap replacement cleanup.

## Important APIs, Types, and Functions
`RemoveOSDs()` is the entry point for purging a list of string OSD IDs. `removeOSD()` performs the step-by-step purge. `removeOSDPrepareJob()` deletes prepare Jobs associated with a PVC-backed OSD. `removePVCs()` deletes or detaches data/db/wal PVCs for one OSD set index. `archiveCrash()` archives Ceph crash entries for the OSD. `DestroyOSD()` destroys a specific OSD and zaps its backing device for replacement flows.

## Control Flow
`RemoveOSDs()` writes Ceph config, fetches OSD dump, parses IDs, skips invalid IDs, skips OSDs still marked up, and calls `removeOSD()` for down OSDs. `removeOSD()` gets the CRUSH host, runs `ceph osd out`, loops on `OsdSafeToDestroy()` with sleeps unless `forceOSDRemoval` allows exit, deletes the OSD deployment, derives the PVC name from deployment labels, removes prepare jobs and PVCs, runs `ceph osd purge`, attempts `ceph osd crush rm <host>`, archives crashes, and logs completion. `DestroyOSD()` fetches OSDInfo, runs `ceph osd destroy`, handles PVC-backed encrypted dm removal and mounted device resolution, then runs `ceph-volume lvm zap --destroy`.

## State and Persistence
This file mutates Ceph cluster maps, Kubernetes Deployments, Jobs, PVCs, CRUSH map entries, crash archive state, dmcrypt devices, and block device metadata. With `preservePVC`, PVCs are detached from Rook by removing the OSD PVC ID label rather than deleted. `DestroyOSD()` reads `ROOK_PVC_NAME` for PVC-backed OSD replacement.

## Dependencies and Integration Points
It depends on Ceph client helpers, Kubernetes clientsets, operator OSD label constants, and `Zap`/encryption helpers from OSD code. It bridges operator-level resources with daemon-side Ceph commands and is sensitive to deployment labels created by the OSD operator.

## Risks
`removeOSD()` logs many errors and continues, so partial cleanup is possible. The safe-to-destroy loop can run indefinitely without force. In `removePVCs()`, the code takes labels from `dataPVC` and deletes the OSD PVC ID label from that shared map inside a loop, then applies it to each PVC; this relies on label shape consistency. `archiveCrash()` appears to log "no ceph crash to silence" when `crash != nil`, then iterates `crash`, which suggests a nil-check logic risk. Force removal bypasses safety and can cause data loss by design.

## Test Signals
`remove_test.go` covers PVC deletion for data-only and data/metadata/wal device sets. It does not cover Ceph command sequences, safe-to-destroy looping, deployment deletion, prepare job deletion, preservePVC label detachment, crash archiving, or `DestroyOSD()`.
