# sources/control-plane/longhorn-engine/integration/data/test_basic_ops.py

## Purpose
Validates basic data-path operations: block device creation, random read/write, metrics, boundary behavior, frontend endpoint reporting, and cleanup of leftover block-device files.

## Important APIs, Types, and Functions
- Tests: `test_device_creation`, `test_basic_rw`, `test_metrics`, `test_beyond_boundary`, `test_frontend_show`, `test_cleanup_leftover_blockdev`.

## Control Flow
Tests start volumes through fixtures, write/read random data at page-aligned offsets, query metrics before and after IO, attempt out-of-bounds writes/reads, inspect CLI `info`, and simulate a leftover blockdev path before volume start.

## State and Persistence Behavior
Creates Longhorn block devices, writes test data to volumes, reads metrics state, and manipulates a placeholder path under `/dev/longhorn`. Boundary test verifies write failure at volume end while controller/replica remain usable.

## Dependencies and Integration Points
Uses `common.cmd.info_get`, `common.core` IO and device helpers, frontend path helper, constants, pytest, and OS filesystem APIs.

## Risks and Edge Cases
Metrics assertions allow retry but require nonzero throughput/IOPS within a short window. Device-name tests rely on `/dev` manipulation and frontend behavior. Out-of-bounds error text `No space left` is environment/API dependent.

## Test Signals
Strong signal for frontend/device integration, controller metrics, IO correctness, boundary handling, and volume info endpoint contract.
