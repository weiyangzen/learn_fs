# sources/control-plane/longhorn-engine/pkg/replica/diff_disk_test.go

Purpose: unit tests core `diffDisk` write alignment and partial-write accounting with an in-memory `types.DiffDisk` mock.

Important APIs/types/functions: `mockDiffDisk` implements `ReadAt`, `WriteAt`, `UnmapAt`, `Size`, `Close`, `Sync`, and `Fd`. Helpers `createTestDiffDisk`, `initializeSector`, and `initializeSectors` build layered test disks. `TestDiffDiskWriteAt` table-tests empty, aligned, unaligned, boundary, and multi-sector writes. `TestComputeNominalWrittenBytes` tests clamping of caller-visible bytes for read-modify-write partial writes.

Control flow: tests create a fresh mock chain per case, optionally prefill sectors and cache locations, execute `WriteAt`, and assert byte counts/errors. Nominal-written tests verify lower bound zero and upper bound buffer size.

State and persistence: uses in-memory byte slices only. Mock `Fd` returns zero, so FIEMAP lookup paths are not meaningfully exercised; tests prepopulate locations where needed.

Dependencies and integration points: directly exercises `diff_disk.go` without filesystem sparse files. Complements `replica_test.go`, which exercises real file behavior.

Risks: the write tests assert counts but do not deeply verify resulting data for every scenario. Mock `WriteAt` fails all write-beyond-size cases with zero bytes, so partial underlying writes are not simulated. FIEMAP and unmap actual-size behavior are outside this file.

Test signals: useful focused coverage for unaligned write decomposition and `computeNominalWrittenBytes`, especially regression protection around partial read-modify-write error reporting.
