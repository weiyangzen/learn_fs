# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.h

Purpose: Declares the vmwgfx DX view/state-object classification interface used by command-buffer resource tracking. It maps SVGA3D create/destroy opcodes to compact driver enums so validation and binding code can manage shader-resource, render-target, depth-stencil, unordered-access views, and state objects consistently.

Important APIs/types: `enum vmw_view_type`, `enum vmw_so_type`, `union vmw_view_destroy`, the view/state cotable lookup tables, and helpers `vmw_view_cmd_to_type()` and `vmw_so_cmd_to_type()`. Exported view APIs add/remove/lookup view resources, destroy view lists, recover the backing surface, and report dirtying behavior.

Control flow: Inline command decoders run on command-parse paths. `vmw_view_cmd_to_type()` relies on opcode ordering and special-cases UA and DSV v2; `vmw_so_cmd_to_type()` explicitly switches state-object create/destroy commands.

State/persistence: Persistent state lives in command-buffer managers, cotables, surfaces, and contexts. The union assumes all view destroy payloads are a single `u32`.

Dependencies/integration: SVGA3D command/cotable definitions, vmwgfx view implementation, binding cleanup, surface destruction, and validation.

Risks/test signals: Opcode-ordering and packed-layout assumptions are fragile. Test unknown opcodes, every view/state-object create/destroy pair, surface teardown with attached views, and header build coverage.
