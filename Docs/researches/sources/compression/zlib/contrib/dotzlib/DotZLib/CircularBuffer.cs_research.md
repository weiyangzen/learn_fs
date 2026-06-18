# sources/compression/zlib/contrib/dotzlib/DotZLib/CircularBuffer.cs

Purpose: provides a small internal byte circular buffer used by DotZLib tests or stream plumbing.

Important APIs/types/functions: `CircularBuffer(int capacity)`, `Size`, `Put(byte[], int, int)`, `Put(byte)`, `Get(byte[], int, int)`, and `Get()`. Internal fields are `_capacity`, `_head`, `_tail`, `_size`, and `_buffer`.

Control flow: construction allocates the fixed-size backing array. Block `Put()` copies up to remaining capacity and wraps each index with modulo arithmetic. Single-byte `Put()` rejects full buffers. Block `Get()` copies up to available size and advances `_head`; single-byte `Get()` returns `-1` when empty.

State and persistence: all state is transient in memory. `_head`, `_tail`, and `_size` represent unread bytes and are mutated on each operation.

Dependencies/integration: depends only on `System` and `System.Diagnostics`. It is internal to the `DotZLib` assembly and directly exercised by `UnitTests.cs`.

Risks: range checks are mostly `Debug.Assert` or absent, so release builds can throw array exceptions or corrupt logical state if callers pass invalid offsets/counts. `_tail` is wrapped after block writes, but `_head++ % _capacity` in `Get()` leaves `_head` unwrapped until later operations, which is logically tolerable for small use but can overflow after very long runs.

Test signals: NUnit-gated `SinglePutGet` and `BlockPutGet` validate empty reads, full-buffer rejection, wraparound, and block copying.
