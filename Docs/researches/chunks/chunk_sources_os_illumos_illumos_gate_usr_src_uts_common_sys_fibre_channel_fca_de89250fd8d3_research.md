# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 59742-63059

## Scope

This chunk is a contiguous slice of the LP11000 Emulex firmware image embedded in `fw_lp11000.h`. It covers source lines 59742-63059, firmware offsets `0x74A20` through `0x7B1C8`, or 26,544 encoded firmware bytes. The file is included through the illumos tree listed in `Docs/research_subset_a.md`.

The content is not C source logic with named functions. It is a byte array containing ARM-style firmware instructions, literal address constants, and embedded trace strings. The report therefore describes the observable firmware behavior and interfaces exposed by the bytecode and strings rather than C-level APIs.

## APIs and Entry Points

- The only C-level surface in this chunk is the surrounding firmware array element stream consumed by the `emlxs` FCA driver when downloading LP11000 firmware to the adapter.
- Firmware-visible entry points are internal branch/call targets encoded as `EB`/`EA` ARM branch opcodes. They are not symbolized here, but the chunk repeatedly calls code outside the range, so it depends on earlier/later firmware routines for logging, timing, queue operations, exchange allocation, buffer release, and link/loop transitions.
- The embedded strings identify internal diagnostic/control surfaces: `Try_OLDP`, `Try_LOOP`, `ACTV %08x`, `Acquire Sync %08x`, `ISSUE LPRQ_INIT`, `LOOP ACTIVE!!!`, `LOSSSYNC`, `CALLILV3`, `CALLILV4`, `Abt Req`, `Fnd abt x`, `Begin RRQ`, `ReQ xcb`, `ReQ dcb`, and `State %02x->%x`.

## Control Flow

The first part continues a routine that was already active before line 59742. Adjacent prior lines show exchange-start/reject diagnostics (`XCB 0: Can't start xchg`, `RJT buf`), and this chunk continues by updating XCB/DCB-like fields, status bytes, and flags before returning or branching into shared firmware routines.

From roughly `0x74E18` through `0x75EF0`, the firmware handles link state and loop/old-port selection. It records/prints attempts to enter old-port or loop mode, checks primitive/status registers, issues LPRQ initialization, and toggles adapter state between "OLDP" and "LOOP" paths. The visible state labels include `TO_LOOP1` through `TO_LOOP6`, `TO_OLDP1`, `TO_OLDP2`, `LOOPACTV`, and `LOOP ACTIVE!!!`.

From roughly `0x75EF8` through `0x76878`, the chunk performs link/event initialization and loop recovery. It sets and clears adapter flags, waits in small delay loops, polls register-like locations, counts retry/timeouts, and writes status bytes around offsets such as `0x30`, `0x39`, `0x44`, `0x48`, `0x50`, `0x60`, and `0x64` in firmware-local structures.

From roughly `0x76878` through `0x77650`, it manages buffer/request allocation and release paths. Embedded diagnostics include `Lbad buffer rls`, `Rls free buf %x`, and `dup get`. The bytecode updates linked-list-looking fields at offsets such as `0x24`, `0x28`, `0x2c`, `0x30`, `0x38`, and array/global counters around `0x138`, `0x220`, `0x224`, `0x228`, and `0x230`.

From roughly `0x77658` through `0x790C8`, the chunk handles abort/request matching. It scans exchange/request tables, checks state bytes and command/status values, emits `Abt Req`, `Fnd abt x`, and `Abt Mtpl`, updates XCB slots and multiple linked queues, and branches into common completion/error paths. It also begins RRQ handling (`Begin RRQ %x->rpi %02x`, `Call new cmd for RRQ sid %08x xid %08x`).

From roughly `0x790F0` through the end of the chunk, it enters broader event/command dispatch code. Several branch tables compare opcodes/state bytes (`0x20`, `0x21`, `0x2b`, `0x84`, `0x86`, `0x88`, `0x8d`, `0x93`, `0x95`, `0x97`, `0x98`, `0x99`, `0x9a`, `0x9c`, etc.) and jump to handlers outside this chunk. The final lines are mid-routine and continue into the next chunk.

## State

The firmware repeatedly treats base pointers as structured regions and mutates fixed offsets. Commonly visible offsets include:

- `0x04`, `0x0c`, `0x1c`, `0x20`, `0x24`, `0x28`, `0x2c`, `0x30`, `0x34`, `0x38`, `0x39`, `0x3e`, `0x40`, `0x44`, `0x48`, `0x4c`, `0x50`, `0x52`, `0x53`, `0x54`, `0x5c`, `0x60`, `0x64`, `0x68`, `0x69`, `0x6c`, `0x72`, `0x73`, `0x78`, `0x80`, `0x88`, `0x8c`, `0x98`, `0xa0`, `0xa3`, `0xa4`, `0xa5`, `0xa7`, `0xa9`, `0xaa`, `0xac`, `0xb0`, `0xb1`, `0xb2`, `0xb9`, `0xbc`, `0xd3`.
- Larger indexed/global offsets include `0x110`, `0x120`, `0x12c`, `0x130`, `0x138`, `0x140`, `0x144`, `0x158`, `0x15c`, `0x180`, `0x184`, `0x19c`, `0x204`, `0x208`, `0x220`, `0x224`, `0x228`, `0x230`, `0x260`, `0x264`, `0x270`, `0x274`, `0x290`, `0x294`, `0x2c0`, `0x2c4`, `0x2d0`, `0x300`, `0x304`, and `0x350`.
- Status/state bytes are compared against many literal values visible in diagnostics and branches: `0x03`, `0x04`, `0x07`, `0x09`, `0x0d`, `0x10`, `0x11`, `0x16`, `0x1d`, `0x20`, `0x25`, `0x26`, `0x2c`, `0x2d`, `0x40`, `0x41`, `0x47`, `0x49`, `0x56`, `0x76`, `0x81`, `0x87`, `0x88`, `0x90`, `0x9b`, `0x9d`, `0xaf`, `0xb0`, `0xb1`, `0xb5`, `0xb7`, `0xb8`, `0xba`, `0xc6`, and `0xc7`.

The visible state machine appears centered on Fibre Channel link/loop state, exchange/request control blocks, DMA/buffer queues, abort/RRQ recovery, and firmware debug counters.

## Dependencies

- This chunk depends on earlier firmware code for the routine that enters at `0x74A20` and for shared branch targets reached by many relative calls.
- It depends on later firmware code because the final routine continues past `0x7B1C8`, and several branch-table cases target addresses beyond this range.
- It depends on adapter memory/register layout: many instructions access magic base constants and fixed offsets rather than self-describing structures.
- Host-side dependency is the illumos `emlxs` driver path that selects and downloads this firmware blob. No Solaris kernel API is directly called by this byte stream.

## Risks and Edge Cases

- The firmware is opaque binary data in a header; normal source review cannot verify invariants, locking, or bounds checks without disassembly and hardware documentation.
- Any byte edit, formatting loss, endian conversion, or truncation would change executable adapter firmware.
- The chunk contains polling/retry/time-out paths (`4 sec t.o.`, loop acquisition, loss of sync) where adapter hangs or long recovery delays are plausible if hardware state does not progress.
- Buffer and exchange management paths include duplicate/free diagnostics, indicating historically important edge cases around double-free, duplicate allocation, and stale XCB/DCB references.
- Abort/RRQ paths scan tables and linked queues; incorrect state transitions could leak exchanges, complete the wrong command, or miss abort completion.
- Branch tables near the end rely on exact opcode/state values; unsupported or corrupted values mostly fall through to shared error paths outside this chunk.

## Cross-Chunk References

- The preceding chunk contains the start of the XCB/exchange routine and diagnostics immediately before this range, including `ABTSbuf`, `RJT buf`, and `XCB 0: Can't start xchg`.
- The next chunk continues the routine cut off at `0x7B1C8`, including literal addresses immediately following this span and further request/queue handling.
- Earlier/later firmware chunks define the common branch targets used here for debug output, command completion, delay/poll loops, link-state helpers, buffer allocation/release, RRQ creation, and error handling.
- The final per-file report should merge this with other chunks as one firmware image rather than as independent C modules.