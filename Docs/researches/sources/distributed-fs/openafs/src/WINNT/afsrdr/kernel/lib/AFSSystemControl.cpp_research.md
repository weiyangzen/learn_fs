# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSystemControl.cpp

## Purpose
`AFSSystemControl.cpp` implements a minimal `IRP_MJ_SYSTEM_CONTROL` handler. It logs the incoming file object, completes the IRP with `STATUS_SUCCESS`, and returns without interpreting WMI/system-control requests.

## Important APIs, Types, And Functions
The file exports `AFSSystemControl(PDEVICE_OBJECT, PIRP)`. It ignores the device object, obtains the current stack location, traces `pIrpSp->FileObject`, completes through `AFSCompleteRequest`, and uses `AFSExceptionFilter` for exception logging.

## Control Flow
There is no branching beyond exception handling: initialize success, get stack, trace, complete, return.

## State And Persistence Behavior
The function has no persistent state and performs no WMI registration, query, update, or forwarding.

## Dependencies And Integration Points
It is a dispatch-table integration point for system-control IRPs and depends only on common redirector tracing/completion infrastructure.

## Risks And Edge Cases
Completing all system-control IRPs successfully with no data may be incompatible with expectations if a WMI client expects registration or pass-through behavior. The file should be checked against the redirector's device-stack design.

## Test Signals
Issue representative system-control/WMI IRPs, verify status and completion, and run verifier-style tests to ensure success-with-no-data is acceptable.
