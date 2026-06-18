# sources/cloud-native/moby/daemon/daemon_windows_test.go

## Purpose
Tests Windows service detection used by daemon system checks.

## Important APIs, Types, And Functions
- `existingService` is the known inbox service `Power`.
- `TestEnsureServicesExist` expects `ensureServicesInstalled` to succeed for the known service.
- `TestEnsureServicesExistErrors` verifies errors for one or more fake service names.

## Control Flow
Each test connects to the Windows service manager, verifies the known service is present, then calls `ensureServicesInstalled` with success and failure inputs. Error tests assert the message names the first missing service encountered.

## State And Persistence
No persistent state is changed; tests only open and close SCM service handles.

## Dependencies And Integration Points
Requires Windows, access to the service manager, and a stable inbox `Power` service. It directly covers `checkSystem`'s service validation helper.

## Risks And Edge Cases
Tests may fail or skip operationally if the process lacks rights to the service manager or if the known service is unavailable on a target image.

## Test Signals
Failures indicate daemon startup may misreport missing Windows container prerequisites or not preserve useful service names in errors.
