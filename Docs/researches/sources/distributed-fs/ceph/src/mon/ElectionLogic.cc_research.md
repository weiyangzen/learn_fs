<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.cc -->
# sources/distributed-fs/ceph/src/mon/ElectionLogic.cc

## Purpose
`ElectionLogic.cc` implements the monitor election decision algorithm independent of monitor messaging and storage details. It tracks election epochs, votes, deferrals, victory validation, disallowed leaders, and connectivity-based leader preference, delegating side effects to `ElectionOwner`.

## Important APIs, types, and functions
Core lifecycle methods are `init()`, `bump_epoch()`, `start()`, `end_election_period()`, `declare_victory()`, `receive_propose()`, `receive_ack()`, and `receive_victory_claim()`. Strategy-specific proposal handlers are `propose_classic_handler()`, `propose_disallow_handler()`, and `propose_connectivity_handler()`. Helpers include `propose_classic_prefix()`, `defer()`, `connectivity_election_score()`, `victory_makes_sense()`, `clear_live_election_state()`, `reset_stable_tracker()`, and `connectivity_bump_epoch_in_election()`.

## Control flow
`start()` initializes or validates the persisted epoch, bumps to an odd election epoch if needed, marks itself as voting for itself, snapshots connectivity state for connectivity elections, sends proposals through the owner, and starts the owner's election timer. Proposals are ignored if self-originated, then routed by strategy. Classic elects lower rank; disallow extends classic by excluding configured ranks; connectivity ranks candidates by disallow status, aggregate connection score, and rank tie-breakers.

When an election timer ends, a node that has a majority of acknowledgements declares victory; otherwise it either starts another election if it has ever participated or asks the owner to reset/bootstrap. Victory bumps to the next even epoch and sends the acked quorum to the owner. Incoming acknowledgements add to `acked_me` only while `electing_me`; acknowledgements from a newer epoch cause a bump and restart. Incoming victory claims must make sense for the strategy and have the expected even epoch, otherwise connectivity mode can bump and restart.

## State and persistence behavior
`epoch` is the persisted election counter read and written through `ElectionOwner`. Odd epochs mean election in progress; even epochs mean stable. `last_election_winner`, `last_voted_for`, `leader_acked`, `electing_me`, `participating`, `acked_me`, `stable_peer_tracker`, and `leader_peer_tracker` are live election state. `bump_epoch()` persists the epoch, updates the peer tracker epoch, clears vote state, and notifies the owner.

## Dependencies and integration points
The logic depends on `ElectionOwner` for persistence, monitor rank/quorum metadata, proposal/ack/victory messaging, election reset, and feature-specific state. Connectivity strategy depends on `ConnectionTracker` score snapshots. `Elector` is the concrete owner in monitor runtime.

## Risks and edge cases
Election correctness depends on all monitors using the same strategy. Connectivity mode has the most subtle invariants: stable snapshots must avoid score changes mid-election, leader tracker comparisons must prevent incompatible deferrals, and out-of-quorum proposal suppression uses an ignore margin to reduce flapping. `receive_ack()` assumes ack epochs are odd. `receive_victory_claim()` records `last_voted_for = leader_acked`, which may be `-1` after unusual state transitions.

## Test signals
Tests should cover first boot epoch initialization, restart from odd persisted epochs, classic rank wins, disallowed leader exclusion, connectivity score tie-breaking, out-of-quorum proposal suppression, majority timeout victory, failed timeout reset, newer-epoch ack restart, invalid victory restart, and standalone victory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.cc -->
