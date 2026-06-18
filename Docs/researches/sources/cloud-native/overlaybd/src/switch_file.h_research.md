## sources/cloud-native/overlaybd/src/switch_file.h

Purpose: declares the switchable file abstraction.

Important APIs: `ISwitchFile` extends Photon `IFile` with `set_switch_file(const char *filepath)`. `new_switch_file(source, local=false, filepath=nullptr)` constructs an implementation, optionally marking the initial source as already local.

Control flow contract: callers use the returned object as an `IFile`; after a local commit/download finishes, they call `set_switch_file` to redirect operations. If initialized as local, operations start on the local file and pread audit applies.

State/persistence: no header state; implementation owns file pointers. Dependencies are Photon filesystem declarations.

Integration points: used by image/layer code that needs transparent source replacement. Risks: raw pointer factory and ownership semantics require callers to delete the returned object; no concurrency contract is documented for switching during active reads. There is no dedicated listed unit test.
