# sources/cloud-native/ostree/src/libostree/ostree-remote.h

## Purpose
This public header declares the opaque `OstreeRemote` API for passing remote configuration handles around libostree and bindings.

## Important APIs, State, and Integration
It declares boxed type registration, `ostree_remote_ref()`, `ostree_remote_unref()`, `ostree_remote_get_name()`, and `ostree_remote_get_url()`. The concrete state remains private, so external callers can only hold references and query basic identity/URL information.

## Risks and Tests
The limited public surface keeps configuration mutation internal, but callers must follow transfer rules: `get_name()` is borrowed and `get_url()` is newly allocated or NULL. Tests should cover boxed type behavior, NULL/invalid remote guard behavior, and memory ownership in bindings.
