# sources/distributed-fs/coda/coda-src/scripts/vice-killvolumes

Purpose: destructive cleanup helper that removes Coda volume database files for a clean start.

Control flow: prompts the operator, accepts yes/default as proceed and no as abort, then removes `/vice/db/VRDB`, `/vice/db/VLDB`, `/vice/vol/RWList`, `/vice/vol/AllVolumes`, `/vice/vol/VolumeList`, and `/vice/db/VRList`, and prints confirmation.

State/persistence: permanently deletes volume database metadata files but does not remove container data or RVM data directly.

Dependencies, risks, tests: depends on fixed `/vice` layout and interactive shell. Risks are obvious destructive behavior, default proceed on empty/unrecognized input, no config-file `vicedir` support, and no backup. Test prompt handling, no branch, removal of missing files, and alternate configured `vicedir` not being honored.
