# sources/distributed-fs/eos/namespace/utils/FileListRandomPicker.hh

## Purpose
Declares the random file picker helper used against namespace filesystem-view file lists. It gives callers a narrow function-level API without exposing the implementation's bucket sampling strategy.

## Important APIs, types, and functions
The single API is `bool pickRandomFile(const IFsView::FileList& filelist, eos::IFileMD::id_t& retval)`. It returns success/failure separately from the selected id, allowing callers to handle empty views without sentinel file ids.

## Control flow
The header has no control flow beyond namespace wrapping. The implementation in the `.cc` file performs empty-list handling and random bucket probing.

## State and persistence
No state is declared. Output is delivered through the `retval` reference.

## Dependencies and integration points
Includes `namespace/Namespace.hh` for the EOS namespace macros and relies on `IFsView::FileList` and `IFileMD::id_t` being available through namespace headers. Consumers include namespace-view utilities and MGM components that need random file sampling.

## Risks and test signals
The declaration hides distribution guarantees, so callers may incorrectly assume uniform random file selection. Tests should pair this header with implementation tests for empty lists, non-empty sampling, and build coverage that ensures all consumers see the required `IFsView` declarations.
