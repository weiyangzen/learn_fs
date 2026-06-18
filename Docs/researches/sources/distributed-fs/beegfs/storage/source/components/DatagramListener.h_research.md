## sources/distributed-fs/beegfs/storage/source/components/DatagramListener.h

Purpose: Declares the storage-specific datagram listener.

Important APIs/types/functions: `DatagramListener` derives from `AbstractDatagramListener`, exposes a constructor/destructor, and overrides protected `handleIncomingMsg()`.

Control flow: Header only defines the class shape.

State and persistence: Runtime network listener state is inherited; no persistent fields are added.

Dependencies and integration: Integrates storage `App` networking with BeeGFS common datagram infrastructure.

Risks and test signals: Behavior resides in cpp. Header risk is mainly API drift with `AbstractDatagramListener`.
