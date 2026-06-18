# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_enc_cfg.h

## Purpose

`link_enc_cfg.h` declares the dynamic DIG link encoder assignment service. It tracks which display endpoints own which DIG encoders, especially where endpoints are mappable or unmappable and where USB4/DPIA changes the traditional PHY relationship.

## Important APIs, Types, And Functions

APIs include `link_enc_cfg_init`, `link_enc_cfg_copy`, assignment and unassignment routines, mappability checks, queries for streams or links using an encoder, query for encoder used by a link or stream, next-available encoder lookup, availability checks, assignment validation, and `link_enc_cfg_set_transient_mode`.

## Control Flow

At state initialization or copy, assignment tables are prepared in `resource_context`. During stream assignment, the algorithm loops over streams twice: first unmappable endpoints, then mappable endpoints. Commit-time transitions can expose both old and new assignments by putting current state into transient mode after validating the new assignment set.

## State And Persistence Behavior

The persistent state is the encoder assignment table and availability list inside DC resource contexts. Transient mode is explicitly stateful and exists so hardware programming can refer to old and new assignments while a commit is in progress.

## Dependencies And Integration Points

The header depends on `core_types.h` and integrates with `link_encoder.h`, resource mapping, link hardware sequencing, DPMS, MST, USB4/DPIA routing, and stream commit state handling.

## Risks And Test Signals

Risks include duplicate encoder ownership, losing an assignment during a transient commit, treating an unmappable endpoint as mappable, or returning stale encoders to link code. Test signals include multi-display DP/HDMI on shared DIG resources, USB4 DPIA links, hotplug during commit, MST changes, validation failures, and debug inspection of assignment tables.
