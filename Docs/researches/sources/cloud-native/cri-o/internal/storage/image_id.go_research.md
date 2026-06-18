# sources/cloud-native/cri-o/internal/storage/image_id.go

Purpose: provides a strongly typed wrapper around full containers/storage image IDs.

Important APIs/types/functions: `StorageImageID`, `ParseStorageImageIDFromOutOfProcessData`, private `parseStorageImageID`, `newExactStorageImageID`, `storageImageIDFromImage`, `ensureInitialized`, `IDStringForOutOfProcessConsumptionOnly`, `Format`, and `imageRef`.

Control flow: constructors validate full identifiers with containers/image reference helpers; zero values panic on use; `imageRef` builds a containers-storage reference for a validated ID.

State and persistence behavior: value type containing a private string. It represents durable storage IDs but does not itself persist anything.

Dependencies and integration points: integrates with `imageService` status/delete/signature paths and CRI out-of-process ID exchange with kubelet.

Risks: zero-value panic is intentional but requires callers to always use constructors. It deliberately avoids `String()` to discourage casual string handling.

Test signals: tests verify valid parsing, invalid input rejection, zero-value panic, `fmt.Formatter` support, and non-implementation of `fmt.Stringer`.
